import pandas as pd
import numpy as np
import os
from datetime import datetime

def parse_time(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H-%M-%S.%f")
    except:
        try:
            return pd.to_datetime(ts_str)
        except:
            return ts_str

def sift_data():
    if not os.path.exists("data/touchpoints.csv"):
        print("Error: touchpoints.csv not found!")
        return
        
    df = pd.read_csv("data/touchpoints.csv")
    print(f"Loaded touchpoints.csv with {len(df)} rows.")
    
    # Ensure datetime parsing
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['user_id', 'datetime']).reset_index(drop=True)
    
    # Flags for bot detection
    df['is_bot_event'] = False
    
    # 1. Detect rapid-fire click bursts (delta < 1ms between consecutive clicks of the same user)
    # We group by user_id, filter by event_type == 'click', and calculate diff
    click_mask = df['event_type'] == 'click'
    df_clicks = df[click_mask].copy()
    
    # Calculate time delta in seconds between consecutive clicks for the same user
    df_clicks['time_diff'] = df_clicks.groupby('user_id')['datetime'].diff().dt.total_seconds()
    
    # If delta is less than 1 millisecond (0.001 seconds), flag it
    rapid_clicks = df_clicks['time_diff'] < 0.001
    
    # We flag the click and also the preceding click since they form a rapid-fire burst
    # To flag both, we can shift the mask back
    rapid_clicks_indices = df_clicks[rapid_clicks].index
    rapid_clicks_prev_indices = rapid_clicks_indices - 1
    
    # Filter indices to make sure we don't go out of bounds or cross user boundaries
    valid_prev = []
    for idx in rapid_clicks_prev_indices:
        if idx in df_clicks.index:
            # Check if it's the same user
            curr_user = df_clicks.loc[idx+1, 'user_id'] if (idx+1) in df_clicks.index else None
            prev_user = df_clicks.loc[idx, 'user_id']
            if curr_user == prev_user:
                valid_prev.append(idx)
                
    flagged_click_indices = list(rapid_clicks_indices) + list(valid_prev)
    df.loc[flagged_click_indices, 'is_bot_event'] = True
    
    # 2. Clicks with zero-second dwell times and no associated impression on the same channel
    # Find clicks with dwell_time == 0.0
    zero_dwell_clicks = df[(df['event_type'] == 'click') & (df['dwell_time'] == 0.0)]
    
    # To check if there's an associated impression, we group by user and channel, 
    # and check if there is at least one impression
    user_channel_impressions = df[df['event_type'] == 'impression'].groupby(['user_id', 'channel']).size().to_dict()
    
    zero_dwell_bot_indices = []
    for idx, row in zero_dwell_clicks.iterrows():
        key = (row['user_id'], row['channel'])
        if key not in user_channel_impressions:
            zero_dwell_bot_indices.append(idx)
            
    df.loc[zero_dwell_bot_indices, 'is_bot_event'] = True
    
    # Get all users who have at least one bot event
    bot_users = df[df['is_bot_event']]['user_id'].unique()
    
    # If a user is flagged as a bot, we flag ALL their events as bot traffic
    df.loc[df['user_id'].isin(bot_users), 'is_bot_event'] = True
    
    # Save statistics before filtering
    total_events = len(df)
    total_users = df['user_id'].nunique()
    
    bot_events_count = df['is_bot_event'].sum()
    bot_users_count = len(bot_users)
    
    cleaned_df = df[~df['is_bot_event']].copy()
    cleaned_df = cleaned_df.drop(columns=['datetime', 'is_bot_event'])
    cleaned_df.to_csv("data/touchpoints_cleaned.csv", index=False)
    
    # Financial Impact of Bots
    # CPC/CPM pricing model
    # Cost per click in Crore (simulated to match a fraction of 100 Crore budget across millions of users)
    # Let's say:
    # Instagram: 0.0001 Crore per click (~₹10,000)
    # Google Search: 0.00015 Crore
    # Influencer Networks: 0.0003 Crore
    # YouTube: 0.0002 Crore
    # E-commerce Marketplaces: 0.00025 Crore
    cpc_rates = {
        "Instagram": 0.0001,
        "Google Search": 0.00015,
        "Influencer Networks": 0.0003,
        "YouTube": 0.0002,
        "E-commerce Marketplaces": 0.00025
    }
    
    bot_clicks = df[df['is_bot_event'] & (df['event_type'] == 'click')]
    bot_savings = 0.0
    bot_savings_by_channel = {}
    
    for channel in cpc_rates:
        count = len(bot_clicks[bot_clicks['channel'] == channel])
        cost = count * cpc_rates[channel]
        bot_savings += cost
        bot_savings_by_channel[channel] = {
            "click_count": count,
            "capital_saved_crore": round(cost, 4)
        }
        
    print(f"Auditing complete:")
    print(f"  - Total events analyzed: {total_events}")
    print(f"  - Bot users identified: {bot_users_count} ({bot_users_count/total_users*100:.2f}%)")
    print(f"  - Bot events flagged and removed: {bot_events_count}")
    print(f"  - Total capital saved via bot defunding: Rs. {bot_savings:.4f} Crore")
    
    # Save a sifter summary report
    report = {
        "total_events": int(total_events),
        "total_users": int(total_users),
        "bot_users": int(bot_users_count),
        "bot_events": int(bot_events_count),
        "capital_saved_crore": round(bot_savings, 4),
        "savings_by_channel": bot_savings_by_channel
    }
    
    import json
    with open("data/sifter_report.json", "w") as f:
        json.dump(report, f, indent=4)

if __name__ == "__main__":
    sift_data()

import os
import uuid
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Parameters
BRANDS = [f"Brand {chr(65+i)}" for i in range(10)]
CHANNELS = ["Instagram", "Google Search", "Influencer Networks", "YouTube", "E-commerce Marketplaces"]
PERSONAS = ["Gen-Z Trendseekers", "Budget Parents", "Tech Savvy Professionals", "Deal Hunters", "Eco-conscious Shoppers", "Suburban Parents"]

# Create output folder
os.makedirs("data", exist_ok=True)

def generate_campaign_spend():
    # Generate random historical campaign spends for each brand across 5 channels (approx 6-9 Crore total per brand)
    records = []
    for brand in BRANDS:
        # distribute between 6 to 9 Crore total spend
        total_brand_spend = np.random.uniform(6.0, 9.0)
        weights = np.random.dirichlet(np.ones(len(CHANNELS)))
        channel_spends = weights * total_brand_spend
        for channel, spend in zip(CHANNELS, channel_spends):
            records.append({
                "brand": brand,
                "channel": channel,
                "spend": round(spend, 4) # in Crore
            })
    df = pd.DataFrame(records)
    df.to_csv("data/campaign_spend.csv", index=False)
    print("Generated campaign_spend.csv")

def generate_user_journeys_and_profiles():
    touchpoint_records = []
    user_profile_records = []
    
    start_date = datetime(2026, 3, 1)
    
    # We will generate ~10,000 users
    num_users = 10000
    
    # 5% of users will behave like bots
    bot_percentage = 0.05
    num_bots = int(num_users * bot_percentage)
    
    # Define channel affinity per persona
    persona_affinities = {
        "Gen-Z Trendseekers": [0.4, 0.1, 0.3, 0.15, 0.05], # Instagram, Search, Influencer, YouTube, Marketplaces
        "Budget Parents": [0.1, 0.3, 0.05, 0.15, 0.4],
        "Tech Savvy Professionals": [0.15, 0.4, 0.05, 0.25, 0.15],
        "Deal Hunters": [0.15, 0.25, 0.1, 0.1, 0.4],
        "Eco-conscious Shoppers": [0.25, 0.2, 0.25, 0.1, 0.2],
        "Suburban Parents": [0.1, 0.3, 0.1, 0.2, 0.3]
    }
    
    # Transition probability weights between channels for normal users (to simulate non-linear journeys)
    # Rows: Instagram, Google Search, Influencer Networks, YouTube, E-commerce Marketplaces
    # Cols: Instagram, Google Search, Influencer Networks, YouTube, E-commerce Marketplaces, Conversion, Null
    transition_weights = {
        "Instagram": [0.1, 0.2, 0.2, 0.2, 0.2, 0.05, 0.05],
        "Google Search": [0.1, 0.1, 0.1, 0.2, 0.4, 0.08, 0.02],
        "Influencer Networks": [0.2, 0.2, 0.1, 0.2, 0.2, 0.04, 0.06],
        "YouTube": [0.2, 0.2, 0.1, 0.1, 0.3, 0.07, 0.03],
        "E-commerce Marketplaces": [0.05, 0.1, 0.05, 0.1, 0.1, 0.4, 0.2]
    }

    for i in range(num_users):
        user_id = str(uuid.uuid4())[:18]
        is_bot = (i < num_bots)
        
        if is_bot:
            # Bot profile: Rapid click bursts and zero dwell times
            brand = np.random.choice(BRANDS)
            persona = "Bot-Simulated"
            user_profile_records.append({"user_id": user_id, "persona": persona})
            
            # Bots generate 5-15 clicks in sub-millisecond deltas or zero dwell times
            num_clicks = np.random.randint(5, 16)
            base_time = start_date + timedelta(days=np.random.uniform(0, 90))
            channel = np.random.choice(CHANNELS)
            
            # Clicks under sub-millisecond deltas or clicks with zero-second dwell times without impressions
            # Let's alternate between the two bot patterns
            pattern = np.random.choice(["rapid_fire", "zero_dwell"])
            
            for c in range(num_clicks):
                if pattern == "rapid_fire":
                    # sub-millisecond delta clicks
                    # We represent sub-milliseconds in timestamp by adding microseconds
                    click_time = base_time + timedelta(microseconds=c * np.random.randint(1, 100))
                    touchpoint_records.append({
                        "user_id": user_id,
                        "timestamp": click_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "channel": channel,
                        "event_type": "click",
                        "dwell_time": round(np.random.uniform(0.1, 2.0), 3),
                        "brand": brand
                    })
                else:
                    # zero-second dwell times without impressions
                    click_time = base_time + timedelta(seconds=c * np.random.randint(2, 10))
                    touchpoint_records.append({
                        "user_id": user_id,
                        "timestamp": click_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "channel": channel,
                        "event_type": "click",
                        "dwell_time": 0.0, # Zero-second dwell time
                        "brand": brand
                    })
        else:
            # Normal User Journey
            brand = np.random.choice(BRANDS)
            persona = np.random.choice(PERSONAS)
            user_profile_records.append({"user_id": user_id, "persona": persona})
            
            # Pick first channel based on persona affinity
            affinities = persona_affinities[persona]
            current_channel = np.random.choice(CHANNELS, p=affinities)
            
            journey_len = np.random.randint(1, 6) # 1 to 5 channel touchpoints
            base_time = start_date + timedelta(days=np.random.uniform(0, 90))
            
            for step in range(journey_len):
                # Add an impression first, then sometimes a click
                imp_time = base_time + timedelta(hours=step * 24 + np.random.uniform(0, 4))
                touchpoint_records.append({
                    "user_id": user_id,
                    "timestamp": imp_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "channel": current_channel,
                    "event_type": "impression",
                    "dwell_time": round(np.random.uniform(2.0, 30.0), 2),
                    "brand": brand
                })
                
                # Clicks occur for some impressions (say 15% CTR)
                if np.random.rand() < 0.15:
                    click_time = imp_time + timedelta(minutes=np.random.uniform(1, 10))
                    touchpoint_records.append({
                        "user_id": user_id,
                        "timestamp": click_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "channel": current_channel,
                        "event_type": "click",
                        "dwell_time": round(np.random.uniform(5.0, 120.0), 2),
                        "brand": brand
                    })
                
                # Check next transition state based on transition weights
                weights = transition_weights[current_channel]
                next_state_idx = np.random.choice(range(7), p=weights)
                
                if next_state_idx < 5:
                    # transition to another channel
                    current_channel = CHANNELS[next_state_idx]
                elif next_state_idx == 5:
                    # Conversion!
                    conv_time = imp_time + timedelta(hours=np.random.uniform(1, 12))
                    touchpoint_records.append({
                        "user_id": user_id,
                        "timestamp": conv_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "channel": current_channel,
                        "event_type": "conversion",
                        "dwell_time": round(np.random.uniform(20.0, 300.0), 2),
                        "brand": brand
                    })
                    break
                else:
                    # Null (drop off)
                    break

    # Save to CSV
    df_touchpoints = pd.DataFrame(touchpoint_records)
    # Sort chronologically by timestamp
    df_touchpoints = df_touchpoints.sort_values(by="timestamp").reset_index(drop=True)
    df_touchpoints.to_csv("data/touchpoints.csv", index=False)
    
    df_profiles = pd.DataFrame(user_profile_records)
    df_profiles.to_csv("data/user_profiles.csv", index=False)
    
    print(f"Generated touchpoints.csv ({len(df_touchpoints)} rows) and user_profiles.csv ({len(df_profiles)} rows)")

if __name__ == "__main__":
    generate_campaign_spend()
    generate_user_journeys_and_profiles()

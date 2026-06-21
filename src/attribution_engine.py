import pandas as pd
import numpy as np
import os
import json

CHANNELS = ["Instagram", "Google Search", "Influencer Networks", "YouTube", "E-commerce Marketplaces"]
BRANDS = [f"Brand {chr(65+i)}" for i in range(10)]

# Assume conversion revenue value in Crore (e.g. Rs. 20,000 per conversion = 0.002 Crore)
REVENUE_PER_CONVERSION = 0.002

def run_attribution():
    if not os.path.exists("data/touchpoints_cleaned.csv") or not os.path.exists("data/campaign_spend.csv"):
        print("Error: Required files not found!")
        return
        
    df_logs = pd.read_csv("data/touchpoints_cleaned.csv")
    df_spend = pd.read_csv("data/campaign_spend.csv")
    
    # Sort chronologically
    df_logs = df_logs.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)
    
    # We will build journeys and run Markov Chain attribution
    # Run globally first, then for each brand
    global_results = analyze_markov_attribution(df_logs, df_spend, label="Global")
    
    brand_results = {}
    for brand in BRANDS:
        df_brand_logs = df_logs[df_logs['brand'] == brand]
        df_brand_spend = df_spend[df_spend['brand'] == brand]
        if len(df_brand_logs) > 0:
            brand_results[brand] = analyze_markov_attribution(df_brand_logs, df_brand_spend, label=brand)
            
    # Save attribution reports
    report = {
        "global": global_results,
        "brands": brand_results
    }
    
    with open("data/attribution_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("Generated attribution_report.json")

def analyze_markov_attribution(df_logs, df_spend, label=""):
    # Reconstruct journeys
    # Group by user_id
    grouped = df_logs.groupby('user_id')
    
    journeys = []
    conversions_count = 0
    
    for user_id, group in grouped:
        # Extract channels in order
        channels_visited = []
        converted = False
        
        for _, row in group.iterrows():
            if row['event_type'] == 'conversion':
                converted = True
            # Collapse consecutive identical channels to avoid self-loops (optional but helps clean matrices)
            ch = row['channel']
            if not channels_visited or channels_visited[-1] != ch:
                channels_visited.append(ch)
                
        if converted:
            conversions_count += 1
            journeys.append(["Start"] + channels_visited + ["Conversion"])
        else:
            journeys.append(["Start"] + channels_visited + ["Null"])
            
    # State mapping
    states = ["Start"] + CHANNELS + ["Conversion", "Null"]
    state_to_idx = {s: i for i, s in enumerate(states)}
    n_states = len(states)
    
    # Count transitions
    transition_counts = np.zeros((n_states, n_states))
    for j in journeys:
        for step in range(len(j) - 1):
            s_from = state_to_idx[j[step]]
            s_to = state_to_idx[j[step+1]]
            transition_counts[s_from, s_to] += 1
            
    # Convert counts to probabilities
    transition_matrix = np.zeros((n_states, n_states))
    for i in range(n_states):
        row_sum = transition_counts[i].sum()
        if row_sum > 0:
            transition_matrix[i] = transition_counts[i] / row_sum
        else:
            # Absorbing states transition to themselves
            transition_matrix[i, i] = 1.0
            
    # Compute conversion probabilities and Removal Effect Index (REI)
    # Transient: Start (0), CHANNELS (1..5)
    # Absorbing: Conversion (6), Null (7)
    # Q is 6x6, R is 6x2
    Q = transition_matrix[:6, :6]
    R = transition_matrix[:6, 6:]
    
    # Fundamental Matrix N = (I - Q)^-1
    I_Q = np.eye(6) - Q
    try:
        N = np.linalg.inv(I_Q)
        B = N @ R
        base_conv_prob = B[0, 0] # Conversion probability from Start
    except np.linalg.LinAlgError:
        # Fallback if I_Q is singular
        N = np.eye(6)
        B = R
        base_conv_prob = B[0, 0]

    # Calculate Removal Effect for each channel
    removal_effects = {}
    for c_idx, channel in enumerate(CHANNELS, start=1):
        # Create a modified transition matrix where channel c_idx transitions to Null with probability 1
        Q_mod = Q.copy()
        R_mod = R.copy()
        
        # Zero out transient transitions for channel c_idx
        Q_mod[c_idx, :] = 0.0
        # Redirect all transitions from channel c_idx to Null
        R_mod[c_idx, 0] = 0.0 # Conversion
        R_mod[c_idx, 1] = 1.0 # Null
        
        # Recompute B_mod = (I - Q_mod)^-1 * R_mod
        I_Q_mod = np.eye(6) - Q_mod
        try:
            N_mod = np.linalg.inv(I_Q_mod)
            B_mod = N_mod @ R_mod
            mod_conv_prob = B_mod[0, 0]
        except np.linalg.LinAlgError:
            mod_conv_prob = 0.0
            
        # Removal Effect
        if base_conv_prob > 0:
            removal_effect = 1.0 - (mod_conv_prob / base_conv_prob)
        else:
            removal_effect = 0.0
        removal_effects[channel] = max(0.0, removal_effect)
        
    # Normalize Removal Effects to get REI
    total_re = sum(removal_effects.values())
    rei = {}
    for channel in CHANNELS:
        if total_re > 0:
            rei[channel] = removal_effects[channel] / total_re
        else:
            rei[channel] = 0.2 # flat prior fallback
            
    # Distribute conversions
    attributed_conversions = {}
    for channel in CHANNELS:
        attributed_conversions[channel] = conversions_count * rei[channel]
        
    # Calculate CPA and ROI
    channel_spends = df_spend.set_index('channel')['spend'].to_dict()
    total_spend = sum(channel_spends.values())
    
    channel_metrics = []
    for channel in CHANNELS:
        spend = channel_spends.get(channel, 0.0)
        convs = attributed_conversions[channel]
        cpa = spend / convs if convs > 0 else 0.0
        
        # Revenue and ROI
        revenue = convs * REVENUE_PER_CONVERSION
        roi_pct = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
        
        channel_metrics.append({
            "channel": channel,
            "spend_crore": round(spend, 4),
            "attributed_conversions": round(convs, 2),
            "cpa_crore": round(cpa, 4),
            "revenue_crore": round(revenue, 4),
            "roi_pct": round(roi_pct, 2),
            "rei": round(rei[channel], 4)
        })
        
    # Funnel Classification: Primers vs Closers
    # Primer Score: Transitions from Start to channel / total visits to channel (from any state)
    # Closer Score: Transitions from channel to Conversion / total transitions out of channel
    funnel_classification = {}
    for c_idx, channel in enumerate(CHANNELS, start=1):
        start_to_c = transition_counts[0, c_idx]
        total_visits_c = transition_counts[:, c_idx].sum()
        c_to_conv = transition_counts[c_idx, 6]
        total_out_c = transition_counts[c_idx].sum()
        
        primer_score = start_to_c / total_visits_c if total_visits_c > 0 else 0.0
        closer_score = c_to_conv / total_out_c if total_out_c > 0 else 0.0
        
        classification = "Primer" if primer_score > closer_score else "Closer"
        funnel_classification[channel] = {
            "primer_score": round(primer_score, 4),
            "closer_score": round(closer_score, 4),
            "classification": classification
        }

    # Format output transition matrix as a list of lists for easy UI consumption
    matrix_list = []
    for i in range(len(states)):
        matrix_list.append({
            "from_state": states[i],
            "transitions": {states[j]: round(transition_matrix[i, j], 4) for j in range(len(states))}
        })

    return {
        "label": label,
        "total_conversions": int(conversions_count),
        "total_spend_crore": round(total_spend, 4),
        "overall_cpa_crore": round(total_spend / conversions_count, 4) if conversions_count > 0 else 0.0,
        "base_conversion_probability": round(base_conv_prob, 4),
        "channel_metrics": channel_metrics,
        "funnel_classification": funnel_classification,
        "transition_matrix": matrix_list
    }

if __name__ == "__main__":
    run_attribution()

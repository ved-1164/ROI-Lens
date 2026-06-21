import os
import json
import pandas as pd
import numpy as np

def run_full_pipeline():
    print("=== Step 1: Run Data Generator ===")
    import generate_data
    generate_data.generate_campaign_spend()
    generate_data.generate_user_journeys_and_profiles()
    
    print("\n=== Step 2: Run Data Sifter (Bot Auditing) ===")
    import data_sifter
    data_sifter.sift_data()
    
    print("\n=== Step 3: Run Attribution Engine (Markov Chains) ===")
    import attribution_engine
    attribution_engine.run_attribution()
    
    print("\n=== Step 4: Run Constrained Portfolio Optimizer ===")
    import optimizer
    optimizer.run_optimization()
    
    print("\n=== Step 5: Aggregate Results for Dashboard ===")
    aggregate_results()

def aggregate_results():
    # Load intermediate results
    with open("data/sifter_report.json", "r") as f:
        sifter = json.load(f)
        
    with open("data/attribution_report.json", "r") as f:
        attribution = json.load(f)
        
    with open("data/optimization_report.json", "r") as f:
        optimization = json.load(f)
        
    # Calculate Persona-Channel Matrix
    # Load cleaned touchpoints and user profiles
    df_logs = pd.read_csv("data/touchpoints_cleaned.csv")
    df_profiles = pd.read_csv("data/user_profiles.csv")
    
    # Merge logs with user profiles to link persona to channel interactions
    df_merged = pd.merge(df_logs, df_profiles, on="user_id", how="inner")
    
    # Create cross tab
    persona_channel_ct = pd.crosstab(df_merged['persona'], df_merged['channel'])
    
    # Convert to JSON dict
    persona_matrix = {}
    for persona in persona_channel_ct.index:
        persona_matrix[persona] = {}
        for channel in persona_channel_ct.columns:
            persona_matrix[persona][channel] = int(persona_channel_ct.loc[persona, channel])
            
    # Combine everything into results.json
    results = {
        "sifter_report": sifter,
        "attribution_report": attribution,
        "optimization_report": optimization,
        "persona_channel_matrix": persona_matrix,
        "meta": {
            "channels": ["Instagram", "Google Search", "Influencer Networks", "YouTube", "E-commerce Marketplaces"],
            "brands": [f"Brand {chr(65+i)}" for i in range(10)],
            "personas": ["Gen-Z Trendseekers", "Budget Parents", "Tech Savvy Professionals", "Deal Hunters", "Eco-conscious Shoppers", "Suburban Parents"]
        }
    }
    
    os.makedirs("dashboard", exist_ok=True)
    with open("dashboard/results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("Aggregate results saved successfully to dashboard/results.json!")

if __name__ == "__main__":
    run_full_pipeline()

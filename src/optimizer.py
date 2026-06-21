import json
import os
import numpy as np
from scipy.optimize import minimize

CHANNELS = ["Instagram", "Google Search", "Influencer Networks", "YouTube", "E-commerce Marketplaces"]
BRANDS = [f"Brand {chr(65+i)}" for i in range(10)]

def run_optimization():
    if not os.path.exists("data/attribution_report.json"):
        print("Error: attribution_report.json not found!")
        return
        
    with open("data/attribution_report.json", "r") as f:
        data = json.load(f)
        
    brands_data = data["brands"]
    optimization_results = {}
    
    total_historical_conversions = 0
    total_optimized_conversions = 0
    total_scaled_historical_conversions = 0
    
    for brand in BRANDS:
        brand_info = brands_data[brand]
        metrics = brand_info["channel_metrics"]
        
        # Fit alpha parameters: alpha = Conversions / ln(Spend + 1)
        alphas = {}
        historical_spends = {}
        historical_conversions = {}
        
        for m in metrics:
            ch = m["channel"]
            spend = m["spend_crore"]
            convs = m["attributed_conversions"]
            
            historical_spends[ch] = spend
            historical_conversions[ch] = convs
            
            if spend > 0:
                alphas[ch] = convs / np.log(spend + 1)
            else:
                alphas[ch] = 0.0
                
        # Total historical Conversions
        total_brand_hist_convs = sum(historical_conversions.values())
        total_historical_conversions += total_brand_hist_convs
        
        # We will run optimization for a 10 Crore budget
        budget_limit = 10.0
        
        # Define objective function: -sum(alpha * ln(x + 1))
        def objective(x):
            val = 0.0
            for i, ch in enumerate(CHANNELS):
                val += alphas[ch] * np.log(x[i] + 1)
            return -val
            
        # Constraint: sum(x) = 10 Crore
        def constraint_budget(x):
            return sum(x) - budget_limit
            
        # Bounds: 0 <= x_c <= 5.0 (cap of 5 Crore per channel to ensure diversification)
        bounds = [(0.0, 5.0) for _ in range(len(CHANNELS))]
        
        # Initial guess (equal distribution)
        x0 = [budget_limit / len(CHANNELS)] * len(CHANNELS)
        
        # Constraints dict
        cons = {'type': 'eq', 'fun': constraint_budget}
        
        # Solve optimization
        res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)
        
        optimized_spends = res.x
        optimized_conversions = -res.fun
        
        # Let's calculate expected conversions if we just scale the historical budget proportions to 10 Crore
        hist_total_spend = sum(historical_spends.values())
        scaled_spends = {}
        expected_scaled_conversions = 0.0
        
        for ch in CHANNELS:
            hist_spend = historical_spends[ch]
            # scale spend proportionally to 10 Crore
            if hist_total_spend > 0:
                scaled_spend = (hist_spend / hist_total_spend) * budget_limit
            else:
                scaled_spend = budget_limit / len(CHANNELS)
            scaled_spends[ch] = scaled_spend
            
            # expected conversions under scaled budget
            expected_scaled_conversions += alphas[ch] * np.log(scaled_spend + 1)
            
        total_optimized_conversions += optimized_conversions
        total_scaled_historical_conversions += expected_scaled_conversions
        
        # Compile channel allocation details
        channel_details = []
        for i, ch in enumerate(CHANNELS):
            channel_details.append({
                "channel": ch,
                "historical_spend": round(historical_spends[ch], 4),
                "historical_conversions": round(historical_conversions[ch], 2),
                "alpha": round(alphas[ch], 4),
                "scaled_historical_spend": round(scaled_spends[ch], 4),
                "optimized_spend": round(optimized_spends[i], 4),
                "expected_optimized_conversions": round(alphas[ch] * np.log(optimized_spends[i] + 1), 2)
            })
            
        # Efficiency gain
        efficiency_gain_pct = ((optimized_conversions - expected_scaled_conversions) / expected_scaled_conversions * 100) if expected_scaled_conversions > 0 else 0.0
        
        optimization_results[brand] = {
            "brand": brand,
            "historical_spend_total": round(hist_total_spend, 4),
            "historical_conversions_total": round(total_brand_hist_convs, 2),
            "scaled_historical_conversions_total": round(expected_scaled_conversions, 2),
            "optimized_conversions_total": round(optimized_conversions, 2),
            "efficiency_gain_pct": round(efficiency_gain_pct, 2),
            "allocations": channel_details
        }
        
    global_efficiency_gain_pct = ((total_optimized_conversions - total_scaled_historical_conversions) / total_scaled_historical_conversions * 100) if total_scaled_historical_conversions > 0 else 0.0
    
    report = {
        "global_historical_conversions": round(total_historical_conversions, 2),
        "global_scaled_historical_conversions": round(total_scaled_historical_conversions, 2),
        "global_optimized_conversions": round(total_optimized_conversions, 2),
        "global_efficiency_gain_pct": round(global_efficiency_gain_pct, 2),
        "brands": optimization_results
    }
    
    with open("data/optimization_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"Optimization completed:")
    print(f"  - Total expected conversions under scaled budget: {total_scaled_historical_conversions:.2f}")
    print(f"  - Total expected conversions under optimized budget: {total_optimized_conversions:.2f}")
    print(f"  - Global Efficiency Gain: {global_efficiency_gain_pct:.2f}%")

if __name__ == "__main__":
    run_optimization()

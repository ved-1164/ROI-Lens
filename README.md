# Project ROI Lens: Advanced Marketing Attribution & Budget Refinement

**Project ROI Lens** is an end-to-end marketing intelligence and budget optimization platform developed for **Nexus Consumer Brands** (a leading FMCG conglomerate). It addresses the legacy "Last-Click" attribution blind spot by implementing a **Multi-Touch Markov Chain Attribution Model** and a **Constrained Portfolio Optimization** solver to maximize campaign efficiency across 10 distinct brands.

---

## 🚀 Key System Features

### 1. 🛡️ Data Sifter (Fraud Auditing)
Eliminates phantom clicks and bot traffic by auditing raw log streams. It flags non-human behavior based on:
* **Rapid-Fire Click Bursts**: Clicks by the same user occurring with a sub-millisecond delta ($< 1\,\text{ms}$).
* **Zero-Dwell Clicks**: Click events with a dwell time of exactly $0$ seconds without an associated impression.
* *Financial Impact*: Filters bot traffic across 500 profiles (5% of users), immediately defunding wasted ad spend and saving **₹1.00 Crore**.

### 🔗 2. Multi-Touch Attribution Engine (Markov Chains)
Replaces primitive last-click logic with a discrete-time absorbing Markov Chain. 
* Models consumer journeys as transition states between channels (*Instagram, Google Search, Influencer Networks, YouTube, E-commerce Marketplaces*), starting at a virtual `Start` state and absorbing into either `Conversion` or `Null` (drop-off).
* Calculates the **Removal Effect Index (REI)** for each channel by computing the fundamental matrix $N = (I - Q)^{-1}$ and absorption probabilities $B = N R$.
* Simulates the deletion of each channel to determine its absolute marginal worth.

### 📊 3. Funnel Role Classification
Classifies channels into structural funnel roles based on multi-stage interaction values:
* **Primers (Top of Funnel)**: High initial awareness catalysts (typically *YouTube* and *Influencer Networks*).
* **Closers (Bottom of Funnel)**: High conversion fulfillment drivers (typically *E-commerce Marketplaces*).

### 📈 4. Ad Fatigue Modeler & Budget Optimizer
Models diminishing returns for channel spends using a saturating logarithmic curve:
$$f(x) = \alpha \cdot \ln(x + 1)$$
* Fits the $\alpha$ coefficients to historical spends and attributed conversions.
* Sets up a constrained optimization problem: Maximize expected conversions for next quarter's ₹100 Crore budget (subject to an exact **₹10 Crore cap per brand** and a **₹5 Crore cap per channel** to ensure diversification).
* Solves using `scipy.optimize.minimize` (SLSQP).
* *Impact*: Delivers a **+323.41% expected efficiency gain** (increasing conversions from 4,134 to 17,504) over proportional historical budget scaling.

### 🖥️ 5. Interactive BI Executive Dashboard
A beautiful, slide-based, glassmorphic dark-theme presentation served locally for Chief Marketing Officer sign-off. It features:
* Clear, interactive metric cards and graphs (using Chart.js).
* An **Interactive Portfolio Planner (Budget Simulator)** where users can manually adjust channel budget sliders and watch expected conversions recompute live against the Markov alphas.

---

## 📂 Repository File Structure

```
├── dashboard/                 # Frontend BI Dashboard
│   ├── index.html             # 9-slide deck layout
│   ├── style.css              # Custom glassmorphic executive styling
│   ├── app.js                 # Chart rendering & interactive budget sliders
│   └── results.json           # Aggregated data exported from Python pipeline
├── data/                      # Raw datasets & intermediate CSVs
│   ├── campaign_spend.csv     # Historical spends per channel/brand
│   ├── touchpoints.csv        # Raw customer journey logs
│   ├── touchpoints_cleaned.csv# Cleaned customer logs (bots removed)
│   ├── user_profiles.csv      # Customer demographic/persona mappings
│   └── sifter_report.json     # Bot traffic audit statistics
├── src/                       # Data Science Python Backend
│   ├── generate_data.py       # Simulates journeys, spends, and bot traffic
│   ├── data_sifter.py         # Audits and cleans logs
│   ├── attribution_engine.py  # Solves Markov Chain REI & Funnel Roles
│   ├── optimizer.py           # Fits log fatigue curves and reallocates budget
│   └── run_pipeline.py        # Orchestrates the pipeline & exports results
├── ROI_Lens.ipynb             # Technical Notebook deliverable
└── README.md                  # Project Documentation
```

---

## 🛠️ Setup and How to Run

### Prerequisites
Make sure you have Python 3 installed with the required libraries:
```bash
pip install pandas numpy scipy matplotlib pypdf
```

### 1. Running the Data Pipeline
To regenerate the synthetic datasets, run the bot auditing, perform the Markov calculations, optimize the portfolio, and export the unified results to the dashboard, run:
```bash
python src/run_pipeline.py
```

### 2. Launching the BI Dashboard
To launch the interactive, slide-deck dashboard, run a local server in the workspace directory:
```bash
python -m http.server 8000 --directory dashboard
```
Open your browser and navigate to:  
👉 **[http://localhost:8000](http://localhost:8000)**

### 3. Launching the Jupyter Notebook
To run the technical codebase step-by-step and view the graphs:
```bash
jupyter notebook ROI_Lens.ipynb
```

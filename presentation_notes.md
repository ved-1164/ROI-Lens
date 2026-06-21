# Project ROI Lens: Concise Step-by-Step Presentation Script

A concise, 9-slide deck structure for the CMO of Nexus Consumer Brands, designed for rapid copy-pasting into Canva.

---

## Slide 1: The Problem (Last-Click Blind Spot)
* **Title**: The Attribution Blind Spot
* **Step**: Step 1 — Contextualizing the Problem
* **Visual**: Graphic of a fractured customer journey path.
* **Bullets**:
  * ₹100 Crore spent across 5 digital channels.
  * Legacy "Last-Click" ignores multi-channel synergies.
  * Suboptimal budget allocations risk millions in revenue.
* **Speaker Script**: *"Legacy Last-Click models ignore the customer journey. We are here to fix this with Project ROI Lens."*

---

## Slide 2: The Audit (Fraud Filtering)
* **Title**: Data Sifter: Fraud Auditing
* **Step**: Step 2 — Sanitizing raw logs
* **Visual**: Large highlight: **₹1.00 Crore Saved** | Pie chart (5% Bots / 95% Clean).
* **Bullets**:
  * Blocked rapid clicks ($< 1\,\text{ms}$ delta).
  * Removed zero-dwell clicks without impressions.
  * Flagged **500 bot users** (5,081 click events).
* **Speaker Script**: *"We cleaned the data. Removing bot clicks immediately saves ₹1.00 Crore in wasted capital."*

---

## Slide 3: The Engine (Markov Attribution)
* **Title**: Probabilistic Attribution Model
* **Step**: Step 3 — Mapping multi-touch pathways
* **Visual**: Grid representation of a transition matrix.
* **Bullets**:
  * Tracks directional migration between channels.
  * Simulates channel removal (Removal Effect Index).
  * Distributes fractional conversion credits mathematically.
* **Speaker Script**: *"We map customer flows as a Markov Chain. We delete channels to calculate their true Removal Effect."*

---

## Slide 4: Funnel Classification (Roles)
* **Title**: Funnel Classification: Primers vs Closers
* **Step**: Step 4 — Channel role mapping
* **Visual**: Two columns: "Primers" vs "Closers".
* **Bullets**:
  * **Primers (Top of Funnel)**: YouTube, Influencers.
  * **Closers (Bottom of Funnel)**: E-commerce, Instagram.
  * Aligns channels to operational customer milestones.
* **Speaker Script**: *"We categorized our channels. YouTube drives awareness, while Marketplaces close the sales."*

---

## Slide 5: Customer Alignment (Personas)
* **Title**: Persona-Channel Interaction Matrix
* **Step**: Step 5 — Segment mapping
* **Visual**: Shaded heat-grid of Personas vs. Channels.
* **Bullets**:
  * Links customer segments with channel affinities.
  * *Gen-Z Trendseekers* engage heavily with Instagram.
  * *Budget Parents* prefer E-commerce Marketplaces.
* **Speaker Script**: *"This heat matrix shows which channels work best for each customer persona."*

---

## Slide 6: Ad Fatigue (Diminishing Returns)
* **Title**: Fatigue Curve & Diminishing ROI
* **Step**: Step 6 — Modeling ad saturation
* **Visual**: Line chart of curves tapering off.
* **Bullets**:
  * Modeled saturation via $f(x) = \alpha \ln(x+1)$.
  * Fits the scaling capacity ($\alpha$) for each channel.
  * Pinpoints where additional spend yields zero return.
* **Speaker Script**: *"Ad networks fatigue. Our curves show exactly when extra spend stops generating conversions."*

---

## Slide 7: Portfolio Reallocation (Optimization)
* **Title**: ₹100 Crore Reallocation Blueprint
* **Step**: Step 7 — Budget optimization
* **Visual**: Highlight: **+323% Expected Conversions** | Comparison table.
* **Bullets**:
  * Solved using SLSQP solver (`scipy.optimize`).
  * Enforces ₹10 Crore brand cap and ₹5 Crore channel cap.
  * Scales expected conversions from 4,134 to 17,504.
* **Speaker Script**: *"By shifting budget out of fatiguing channels, we unlock a 323% gain in total conversions."*

---

## Slide 8: Action Plan (CMO Mandates)
* **Title**: Prescriptive Action Items
* **Step**: Step 8 — Strategic execution
* **Visual**: A 3-step numbered checklist.
* **Bullets**:
  * **1. Defund Bots**: IP-block rapid click loops (saves ₹1 Crore).
  * **2. Enforce Caps**: Apply ₹5 Crore channel caps per brand.
  * **3. Rebalance Spends**: Move budget from saturated slots to primers.
* **Speaker Script**: *"Our action mandates: Block bot fraud, enforce channel caps, and rebalance spends."*

---

## Slide 9: BI Roadmap (Scale)
* **Title**: BI Dashboard Scale Roadmap
* **Step**: Step 9 — Future productization
* **Visual**: A 3-step Q3 -> Q4 -> Q1 timeline.
* **Bullets**:
  * **Q3 2026**: Automated Facebook & Google API connectors.
  * **Q4 2026**: Live streaming Markov calculations on Spark.
  * **Q1 2027**: Direct DSP bidding API integrations.
* **Speaker Script**: *"We will scale this offline audit into a real-time live BI dashboard by next year."*

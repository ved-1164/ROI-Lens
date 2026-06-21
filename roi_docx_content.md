The synthetic logic applied:
Cost Savings ($): Calculated as a factor of the volume of content created via AI compared to manual video editing costs (approx. $45–$50 saved per short video created).
Estimated ROI (%): Derived from the ratio of "Value of Published Content" vs. the "AI Platform Cost" to generate that volume of content.
Human Labor Saved (Hrs): Estimates the time returned to the media team based on a 1.25–1.5 hour manual editing time per short-form video.
Generated Synthetic Files
The following files are now available, categorized by your requested filters:
Date Range / Time-Series
synthetic_monthly_roi_report.csv: Tracks monthly progression of cost savings and ROI percentages.
synthetic_monthly_duration_roi.csv: Provides savings metrics based on the total duration of content created and published.
User Performance
synthetic_user_roi_metrics.csv: Shows which users are generating the highest return on investment through platform efficiency.
Video / Input Type
synthetic_content_type_roi.csv: Breaks down ROI by content category (e.g., Interviews, News Bulletins, Speeches).
Company / Channel
synthetic_client_roi_summary.csv: A high-level view for clients showing channel-wise savings.
synthetic_roi_by_channel and user.csv: A granular breakdown of ROI per user within specific channels.
Language & Dimension
synthetic_roi_by_language.csv: Compares ROI across different content languages.
synthetic_roi_by_output type.csv: Analyzes ROI based on output dimensions (e.g., Key Moments vs. Full Packages).
To provide a clear understanding of how your B2B AI platform's data was transformed into business-centric metrics, here is a step-by-step explanation of the logic and the code implementation.
1. Defining the Core Business Logic
The generation of synthetic data isn't random; it follows a "Value Attribution" model. Instead of looking at raw counts (how many videos were made), we calculate the economic impact of those actions.
Cost Savings ($): We assume that every short-form video created by the AI replaces a manual editing task that would typically cost a company approximately $\$45$.$$\text{Cost Savings} = \text{Created Count} \times 45$$
Human Hours Saved: We estimate that a manual editor takes about $1.25$ hours to identify, clip, and format a high-quality short from long-form content.$$\text{Human Hours Saved} = \text{Created Count} \times 1.25$$
Estimated ROI (%): ROI is calculated by comparing the "Return" (Value of Published Content) against the "Investment" (Cost of Platform usage/Creation effort). To ensure the data looks realistic, we add a small constant to the denominator to prevent division by zero.$$\text{ROI} = \left( \frac{\text{Published Count} \times 200}{\text{Created Count} \times 5 + 10} \right) \times 100$$
Getty Images
2. The Transformation Engine (transform_df function)
The code uses a central function to handle the bulk of the CSV files. This ensures consistency across different filters (User, Language, Channel).
Metric Injection: The function takes an input DataFrame and creates the three new columns using the formulas above.
Column Cleanup: To make the data truly "synthetic," the code removes the original Created Count and Published Count columns.
Duration Filtering: The function automatically scans for any columns containing the word "Duration" (like Created Duration) and drops them to ensure the output focuses strictly on financial metrics.

3. Handling Time and Durations
Two of your files (month-wise-duration.csv and channel-wise-publishing duration.csv) contained time strings in hh:mm:ss format. Raw strings cannot be used in math, so the code employs a helper:
duration_to_hours: This function splits the string (e.g., "01:30:00") into hours, minutes, and seconds and converts them into a decimal number (e.g., $1.5$ hours).
Value Multipliers: For duration-based files, we apply higher multipliers. For instance, we estimate $\$150$ in savings for every $1$ hour of finished content produced by the AI.

4. The Data Pipeline Execution
The script follows a standard Extract-Transform-Load (ETL) pipeline:

Shutterstock
Explore
Extraction: The code loops through the list of uploaded files (Monthly, User, Language, etc.) using pd.read_csv().
Transformation:
It identifies which columns represent "Created" and "Published" data.
It applies the transform_df function or the duration-specific logic.
It rounds percentages and dollar amounts to two decimal places for professional reporting.
Loading: The final step uses to_csv() to write the modified data into new files with the synthetic_ prefix, leaving your original data untouched.
5. Why this is useful
By shifting the data from Activity Metrics (Counts/Durations) to Outcome Metrics (Savings/ROI), the platform's value becomes immediately apparent to stakeholders:
Media Managers can see how much time their team saved.
CFOs can see the direct cost-benefit of the AI subscription.
Operations can identify which channels or languages are yielding the highest return on effort.

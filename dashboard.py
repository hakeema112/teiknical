# this file is AI generated
import os
import shutil
import analysis
 
DB_PATH = "cell_count.db"
OUTPUT_DIR = "output"
DOCS_DIR = "docs"  # GitHub Pages can only serve from root or /docs
 
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Loblaw Bio - Immune Cell Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f7f7f9;
            color: #222;
        }}
        h1 {{ margin-bottom: 0; }}
        .subtitle {{ color: #666; margin-top: 4px; }}
        section {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 12px;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 6px 10px;
            text-align: left;
        }}
        th {{ background-color: #eee; }}
        .note {{ color: #666; font-size: 13px; margin-top: 8px; }}
        img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 12px; }}
        .significant {{ color: #1a7a1a; font-weight: bold; }}
        .not-significant {{ color: #999; }}
    </style>
</head>
<body>
    <h1>Immune Cell Population Dashboard</h1>
    <p class="subtitle">Cell count analysis for Bob Loblaw's clinical trial (miraclib, melanoma)</p>
 
    <section>
        <h2>Part 2: Cell Population Frequency by Sample</h2>
        <p>Relative frequency of each immune cell population within each sample.</p>
        {freq_table_html}
        <p class="note">Showing first 50 of {freq_total_rows} rows. Full table: <a href="frequency_table.csv">frequency_table.csv</a></p>
    </section>
 
    <section>
        <h2>Part 3: Responders vs Non-Responders</h2>
        <p>Melanoma patients treated with miraclib (PBMC samples only), comparing relative
        cell population frequencies between responders and non-responders.</p>
        <h3>Statistical results (Mann-Whitney U test, Bonferroni-corrected)</h3>
        {stats_table_html}
        <p class="{significance_class}">{significance_message}</p>
        <h3>Boxplot</h3>
        <img src="responder_boxplot.png" alt="Responder vs non-responder boxplot">
    </section>
 
    <section>
        <h2>Part 4: Baseline Melanoma + Miraclib + PBMC Subset</h2>
        <p>Samples taken at baseline (time_from_treatment_start = 0) from melanoma
        patients treated with miraclib.</p>
 
        <h3>Samples per project</h3>
        {samples_per_project_html}
 
        <h3>Responders vs non-responders (unique subjects)</h3>
        {responders_per_subject_html}
 
        <h3>Sex breakdown (unique subjects)</h3>
        {sex_per_subject_html}
    </section>
</body>
</html>
"""
 
 
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    # ---- Part 2 ----
    freq_df = analysis.frequency_table(DB_PATH)
    freq_table_html = freq_df.head(50).to_html(index=False, classes="dataframe")
 
    # ---- Part 3 ----
    filtered, results = analysis.compare(DB_PATH)
    stats_table_html = results.to_html(index=False, classes="dataframe")
    analysis.boxplot(filtered, save_path=os.path.join(OUTPUT_DIR, "responder_boxplot.png"))
 
    significant = results[results["significant"]]
    if len(significant) > 0:
        significance_class = "significant"
        significance_message = (
            f"Significant populations (alpha=0.05, corrected): "
            f"{', '.join(significant['population'].tolist())}"
        )
    else:
        significance_class = "not-significant"
        significance_message = (
            "No population reached statistical significance after Bonferroni "
            "correction in this cohort."
        )
 
    # ---- Part 4 ----
    samples_per_project, responders_per_subject, sex_per_subject = analysis.summary(DB_PATH)
 
    # ---- write everything out ----
    html = HTML_TEMPLATE.format(
        freq_table_html=freq_table_html,
        freq_total_rows=len(freq_df),
        stats_table_html=stats_table_html,
        significance_class=significance_class,
        significance_message=significance_message,
        samples_per_project_html=samples_per_project.to_html(index=False, classes="dataframe"),
        responders_per_subject_html=responders_per_subject.to_html(index=False, classes="dataframe"),
        sex_per_subject_html=sex_per_subject.to_html(index=False, classes="dataframe"),
    )
 
    # also save the CSVs referenced by the page, so the link works
    freq_df.to_csv(os.path.join(OUTPUT_DIR, "frequency_table.csv"), index=False)
    results.to_csv(os.path.join(OUTPUT_DIR, "responder_stats.csv"), index=False)
    samples_per_project.to_csv(os.path.join(OUTPUT_DIR, "samples_per_project.csv"), index=False)
    responders_per_subject.to_csv(os.path.join(OUTPUT_DIR, "responders_per_subject.csv"), index=False)
    sex_per_subject.to_csv(os.path.join(OUTPUT_DIR, "sex_per_subject.csv"), index=False)
 
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(html)
 
    print(f"Dashboard written to {OUTPUT_DIR}/index.html")
 
    # ---- also copy everything into docs/, for GitHub Pages ----
    # GitHub Pages can only serve from the repo root or a /docs folder,
    # so we mirror the output/ folder there automatically on every run.
    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
    shutil.copytree(OUTPUT_DIR, DOCS_DIR)
 
    print(f"Dashboard also copied to {DOCS_DIR}/ for GitHub Pages")
 
 
if __name__ == "__main__":
    main()
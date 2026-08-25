import os
import load_data
import analysis
import dashboard
 
DB_PATH = "cell_count.db"
OUTPUT_DIR = "output"
 
# main script that runs the whole pipeline
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    # Part 1: build the database
    print("Step 1/4: Building the database...")
    load_data.main()
 
    # Part 2: frequency table 
    print("Step 2/4: Generating frequency table...")
    freq_table = analysis.frequency_table(DB_PATH)
    freq_table.to_csv(os.path.join(OUTPUT_DIR, "frequency_table.csv"), index=False)
 
    # Part 3: responder comparison + boxplot 
    print("Step 3/4: Comparing responders vs non-responders...")
    filtered, results = analysis.compare(DB_PATH)
    results.to_csv(os.path.join(OUTPUT_DIR, "responder_stats.csv"), index=False)
    analysis.boxplot(filtered, save_path=os.path.join(OUTPUT_DIR, "responder_boxplot.png"))
 
    # Part 4: baseline subset summaries 
    print("Step 4/4: Generating baseline subset summaries...")
    samples_per_project, responders_per_subject, sex_per_subject = analysis.summary(DB_PATH)
    samples_per_project.to_csv(os.path.join(OUTPUT_DIR, "samples_per_project.csv"), index=False)
    responders_per_subject.to_csv(os.path.join(OUTPUT_DIR, "responders_per_subject.csv"), index=False)
    sex_per_subject.to_csv(os.path.join(OUTPUT_DIR, "sex_per_subject.csv"), index=False)

    # Dashboard: build the static HTML page from everything above
    print("Building dashboard...")
    dashboard.main()

    print(f"\nDone. All outputs saved to {OUTPUT_DIR}/")
 
 
if __name__ == "__main__":
    main()
import sqlite3
import pandas as pd  # to parse the csv

CSV_PATH = "cell-count.csv"
DB_PATH = "cell_count.db"
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def main():
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    load_data(conn, CSV_PATH)
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")


def create_schema(conn):
    cursor = conn.cursor()

    # Drop tables if they already exist, so re-running the script is clean/idempotent
    cursor.execute("DROP TABLE IF EXISTS samples")
    cursor.execute("DROP TABLE IF EXISTS subjects")

    # One row per patient. treatment/response are stored here because they
    # are constant across all of a subject's samples in this dataset.
    cursor.execute("""
        CREATE TABLE subjects (
            subject_id TEXT PRIMARY KEY,
            project TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT
        )
    """)

    # One row per blood draw (sample), linked back to the subject it came from.
    # Counts stay as columns here (wide format) rather than a separate table.
    cursor.execute("""
        CREATE TABLE samples (
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            b_cell INTEGER,
            cd8_t_cell INTEGER,
            cd4_t_cell INTEGER,
            nk_cell INTEGER,
            monocyte INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
        )
    """)

    conn.commit()


def load_data(conn, csv_path):
    df = pd.read_csv(csv_path)

    # ---- subjects table ----
    # One row per unique subject_id. drop_duplicates keeps the first
    # occurrence, which is fine since these fields don't vary per subject.
    subjects_df = (
        df[["subject", "project", "condition", "age", "sex", "treatment", "response"]]
        .drop_duplicates(subset=["subject"])
        .rename(columns={"subject": "subject_id"})
    )
    subjects_df.to_sql("subjects", conn, if_exists="append", index=False)

    # ---- samples table ----
    # Keep counts as columns (wide format) instead of a separate cell_counts table.
    samples_df = (
        df[["sample", "subject", "sample_type", "time_from_treatment_start"] + POPULATIONS]
        .rename(columns={"sample": "sample_id", "subject": "subject_id"})
    )
    samples_df.to_sql("samples", conn, if_exists="append", index=False)

# need this to run the script from the command line, otherwise nothing happens
if __name__ == "__main__":
    main()
import sqlite3
import pandas as pd
from scipy.stats import mannwhitneyu

DB_PATH = "cell_count.db"
POPULATIONS = [ "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte" ]

# Part 2:
def frequency_table(DB_PATH):
    conn = sqlite3.connect(DB_PATH)

    # get samples table
    df = pd.read_sql_query("SELECT * FROM samples", conn)
    conn.close()

    # sum the 5 population columns
    df["total_count"] = df[POPULATIONS].sum(axis=1)

    # need long format
    long_df = df.melt(
        id_vars=['sample_id', 'total_count'],
        value_vars=POPULATIONS,
        var_name='population',
        value_name='count'
    )

    # percentage: count / total_count * 100
    long_df["percentage"] = (long_df["count"] / long_df["total_count"]) * 100

    # rename sample_id
    long_df = long_df.rename(columns={"sample_id": "sample"})

    # order columns
    long_df = long_df[["sample", "total_count", "population", "count", "percentage"]]

    return long_df

# Part 3:
def compare(DB_PATH):
    # need to filter to keep only rows matching melanoma and miraclib and pbmc
    # get a column of t/f where all three (melanoma, miraclib, pbmc) are true, then filter the df to keep only those rows
    df = join(DB_PATH)
    filtered = df[
        (df["condition"] == "melanoma")
        & (df["treatment"] == "miraclib")
        & (df["sample_type"] == "PBMC")
    ]

    results = [] # placeholder for results of the statistical tests

    # loop throuhg each pop, splitting responders vs non responders
    for pop in POPULATIONS:
        pop_df = filtered[filtered["population"] == pop]

        responders = pop_df[pop_df["response"] == "yes"]["percentage"]
        non_responders = pop_df[pop_df["response"] == "no"]["percentage"]

        # run the Mann-Whitney U test: line below was AI auto-generated
        stat, p_value = mannwhitneyu(responders, non_responders, alternative="two-sided")
        # Bonferroni correction: line below was AI auto-generated
        corrected_p = min(p_value * len(POPULATIONS), 1.0)

        results.append({
            "population": pop,
            "n_responders": len(responders),
            "n_non_responders": len(non_responders),
            "u_statistic": stat,
            "p_value": p_value,
            "p_value_bonferroni": corrected_p,
            "significant": corrected_p < 0.05,
        })

    results_df = pd.DataFrame(results)
    # filtered is the data for the boxplot, results_df is the statistical test results
    return filtered, results_df

def join(DB_PATH):
    frequency_df = frequency_table(DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    # need to join subject and sample metadata so we can filter by them
    meta_df = pd.read_sql_query("""
        SELECT
            samples.sample_id AS sample,
            samples.sample_type,
            samples.time_from_treatment_start,
            subjects.subject_id,
            subjects.project,
            subjects.condition,
            subjects.age,
            subjects.sex,
            subjects.treatment,
            subjects.response
        FROM samples
        JOIN subjects ON samples.subject_id = subjects.subject_id
    """, conn)
    conn.close()

    return frequency_df.merge(meta_df, on="sample", how="left")

def boxplot(filtered, save_path="responder_boxplot.png"):
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.boxplot(
        data=filtered,
        x="population",
        y="percentage",
        hue="response",
        ax=ax,
    )

    ax.set_title("Cell Population Frequency: Responders vs Non-Responders")
    ax.set_xlabel("Cell Population")
    ax.set_ylabel("Relative Frequency (%)")
    ax.legend(title="Response")

    fig.tight_layout()
    fig.savefig(save_path)

    return fig

# Part 4:


# testing:
if __name__ == "__main__": # sanity check: DELETEME
    # table = frequency_table(DB_PATH)
    # print(table.head(15))
    # print(f"\nTotal rows: {len(table)}")

    print("\n--- Part 3: Responders vs Non-Responders (melanoma, miraclib, PBMC) ---")
    filtered, results = compare(DB_PATH)
    print(results)

    boxplot(filtered)
    print("\nBoxplot saved to responder_boxplot.png")
import sqlite3
import pandas as pd

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

# also for part 2:
if __name__ == "__main__": # sanity check: DELETEME
    table = frequency_table(DB_PATH)
    print(table.head(15))
    print(f"\nTotal rows: {len(table)}")

# Part 3:

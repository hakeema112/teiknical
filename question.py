import sqlite3
import pandas as pd

conn = sqlite3.connect("cell_count.db")

df = pd.read_sql_query("""
    SELECT samples.b_cell
    FROM samples
    JOIN subjects ON samples.subject_id = subjects.subject_id
    WHERE subjects.condition = 'melanoma'
      AND subjects.sex = 'M'
      AND subjects.response = 'yes'
      AND samples.time_from_treatment_start = 0
""", conn)

conn.close()

print(f"n = {len(df)}")
print(f"Average b_cell count: {df['b_cell'].mean():.2f}")
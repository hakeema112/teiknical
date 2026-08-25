# Loblaw Bio - Immune Cell Population Analysis

Analysis pipeline and dashboard for Bob Loblaw's clinical trial data, examining
how immune cell populations relate to treatment response.

**Dashboard:** https://hakeema112.github.io/teiknical/

## How to Run

```bash
make setup      # installs dependencies from requirements.txt
make pipeline   # builds the database and runs the full analysis (Parts 1-4)
make dashboard  # serves the dashboard locally at http://localhost:8000
```

`make pipeline` is fully automated — it initializes the SQLite database, loads
`cell-count.csv`, and generates every output table and plot into the `output/`
folder. No manual steps are required between commands.

### Requirements

- Python 3
- `cell-count.csv` present in the repository root

## Database Schema

The data is modeled as two tables in `cell_count.db`:

**`subjects`** — one row per patient:

| column | type | notes |
|---|---|---|
| subject_id | TEXT (PK) | |
| project | TEXT | |
| condition | TEXT | e.g. melanoma, carcinoma |
| age | INTEGER | |
| sex | TEXT | |
| treatment | TEXT | e.g. miraclib |
| response | TEXT | yes/no |

**`samples`** — one row per blood draw, linked to a subject:

| column | type | notes |
|---|---|---|
| sample_id | TEXT (PK) | |
| subject_id | TEXT (FK -> subjects) | |
| sample_type | TEXT | e.g. PBMC |
| time_from_treatment_start | INTEGER | |
| b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte | INTEGER | raw cell counts |

### Design rationale

The raw CSV mixes two levels of information in every row: facts about a
*patient* (age, condition, treatment, response) that don't change across
their visits, and facts about a single *blood draw* (timepoint, cell counts)
that do. Splitting these into two tables avoids repeating a patient's
metadata once per sample, and reflects the real one-to-many relationship
between a subject and their samples (one subject can contribute multiple
samples, e.g. at days 0, 7, and 14).

Cell counts were kept as columns on `samples` (rather than a third,
fully-normalized `cell_counts` table with one row per sample+population)
to keep the schema simpler for this assignment's scope, given that there
are a small, fixed number of populations. The trade-off is discussed below.

### Scaling considerations

If this dataset grew to hundreds of projects, thousands of samples, and a
wider range of analyses, a few changes would matter:

- **Normalize cell counts into their own table** (`cell_counts`: sample_id,
  population, count), rather than columns on `samples`. Right now adding a
  6th cell population would mean an `ALTER TABLE`; in a long-format table
  it's just new rows, which supports assays with different or evolving
  panels of populations.
- **Add indexes** on foreign keys (`samples.subject_id`) and frequently
  filtered columns (`condition`, `treatment`, `response`, `sample_type`,
  `time_from_treatment_start`), since the queries in this project all
  filter or join on those fields.
- **Move off SQLite** to a server-based database (e.g. Postgres) once
  multiple users or automated pipelines need concurrent read/write access,
  since SQLite is a single local file not designed for concurrent writers.
- **Separate raw data from derived results.** Currently the frequency
  table and statistical comparisons are recomputed from scratch each run.
  At scale, storing precomputed summary tables (refreshed on a schedule
  or on data change) would avoid re-scanning the full raw dataset for
  every dashboard view.
- **Add a `projects` table** if project-level metadata grows beyond a
  single label (e.g. study phase, sponsor, start date), rather than
  keeping `project` as a plain text column on `subjects`.

## Code Structure

| file | purpose |
|---|---|
| `load_data.py` | Part 1. Creates `cell_count.db` and loads `cell-count.csv` into the `subjects`/`samples` schema. Run directly: `python load_data.py`. |
| `analysis.py` | Reusable analysis functions for Parts 2-4 (frequency table, responder comparison + stats + boxplot, baseline subset summaries). Imported by both `pipeline.py` and `dashboard.py` rather than duplicating logic in each. |
| `dashboard.py` | Builds a static HTML dashboard (`output/index.html`) from the functions in `analysis.py`. |
| `pipeline.py` | Orchestrates the full pipeline end-to-end: builds the database, runs all analyses, writes every output table/plot, and generates the dashboard. This is what `make pipeline` calls. |
| `requirements.txt` | Python dependencies for `make setup`. |
| `Makefile` | `setup` / `pipeline` / `dashboard` targets, as required. |

### Why this structure

`load_data.py` is kept minimal and focused since it has a hard requirement
to be named exactly that and runnable with no arguments. `analysis.py` holds
all the actual data-crunching as plain functions (not scripts) so the exact
same code can be called from a one-off pipeline run or from the dashboard,
without maintaining two copies of the same logic. `pipeline.py` is the single
entry point that ties everything together in order, matching the assignment's
requirement that `make pipeline` runs the whole thing with no manual
intervention. The dashboard is a static HTML page (rather than a live
server-rendered app) generated once per pipeline run and served with
Python's built-in `http.server` — this keeps the `make dashboard` target
simple and dependency-light.

## Part 3 Findings

Comparing relative cell population frequencies between miraclib-treated
melanoma responders and non-responders (PBMC samples only), using a
Mann-Whitney U test per population with Bonferroni correction for multiple
comparisons: no population reached statistical significance at alpha=0.05
after correction in this cohort. `cd4_t_cell` showed the strongest trend
(raw p ~0.013, corrected p ~0.067), closest to the threshold and worth
revisiting with a larger cohort. Full results and the comparison boxplot
are in `output/responder_stats.csv` and `output/responder_boxplot.png`.

Note: each sample (including multiple timepoints per subject) was treated
as an independent observation in this comparison. A stricter analysis might
collapse to one value per subject (e.g. baseline only, or averaged across
timepoints) before testing, since samples from the same subject aren't
fully independent of each other.

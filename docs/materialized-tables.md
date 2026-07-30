# Materialized Dashboard Tables

The `v_*` views parse JSON on every query. That is fine while
`prompt_run_results` is small, but as scheduled runs accumulate data, each
Looker Studio refresh re-scans and re-parses the whole table.

`sql/migrations/v0.4.0_materialize_dashboard_tables.sql` snapshots the views
into partitioned, clustered tables:

| Table | Source view | Partition | Cluster |
|-------|-------------|-----------|---------|
| `t_visibility_daily` | `v_visibility_daily` | `run_date` | `provider` |
| `t_brand_mentions` | `v_brand_mentions` | `run_date` | `brand, provider` |
| `t_citations` | `v_citations` | `run_date` | `citation_domain` |

## When to switch

Stay on the `v_*` views until dashboard refreshes feel slow or query costs
become noticeable (roughly: tens of thousands of rows in
`prompt_run_results`). Then point Looker Studio at the `t_*` tables instead —
the column names are identical, so charts only need their data source
swapped.

## Setup

### 1. Create the tables once

Open the SQL file, replace `your-project.your_dataset` with your values, and
run it in the BigQuery console. Three tables are created.

### 2. Schedule the refresh

1. In the BigQuery console, open the same query and click
   **Schedule** (top bar) > **Create new scheduled query**.
2. Name: `refresh dashboard tables`.
3. Schedule: daily, at a time after your prompt runs finish
   (e.g. 07:00 Asia/Tokyo if the scheduler runs at 06:00).
4. Leave "Destination table" empty — the script writes tables itself.
5. Save. BigQuery re-runs the script daily and the `t_*` tables stay fresh.

### 3. Repoint Looker Studio (when needed)

In each Looker Studio data source, click **Edit connection** and select the
`t_*` table matching the view it used before. No chart changes are required.

## Notes

- `CREATE OR REPLACE TABLE ... AS SELECT` performs a full rebuild. At very
  large scale, convert the scheduled query to an incremental `MERGE` on
  recent `run_date` partitions.
- The views remain the source of truth; the tables are disposable snapshots
  and can be rebuilt at any time.

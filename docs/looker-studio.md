# Looker Studio Dashboard Setup

This guide connects Looker Studio to the BigQuery analysis views so you can
monitor brand visibility across LLM providers over time.

## Prerequisites

1. Results are being stored in BigQuery (`RESULT_REPOSITORY=bigquery`).
2. The v0.2.0 migration has been applied
   (`sql/migrations/v0.2.0_add_analysis_columns.sql`).
3. The analysis views have been created
   (`sql/migrations/v0.3.0_create_analysis_views.sql`).

The views used by the dashboard:

| View | Grain | Purpose |
|------|-------|---------|
| `v_visibility_daily` | 1 row per day x provider | Target score & share of voice trend |
| `v_brand_mentions` | 1 row per brand x prompt execution | Brand comparison, ranks, sentiment |
| `v_citations` | 1 row per citation URL | Which sources AI search cites |

## Connect the data sources

1. Open [Looker Studio](https://lookerstudio.google.com/) and sign in with the
   Google account that has access to your GCP project.
2. Create > Data source > **BigQuery**.
3. Select your project > dataset > `v_visibility_daily` > **Connect**.
4. Repeat for `v_brand_mentions` and `v_citations`.

## Recommended dashboard pages

### Page 1: Visibility trend

- **Time series chart** — data source `v_visibility_daily`
  - Dimension: `run_date`
  - Breakdown dimension: `provider`
  - Metric: `avg_target_score`
- **Scorecard** — `avg_share_of_voice` (latest date filter)

### Page 2: Brand comparison

- **Bar chart** — data source `v_brand_mentions`
  - Dimension: `brand`
  - Metric: AVG(`visibility_score`)
- **Table** — dimensions `brand`, `provider`;
  metrics AVG(`visibility_score`), AVG(`rank`), COUNT(`result_id`)
- **Stacked bar (sentiment)** — dimension `brand`,
  breakdown `sentiment`, metric Record Count

### Page 3: Citations (AI search sources)

- **Table** — data source `v_citations`
  - Dimension: `citation_domain`
  - Metric: Record Count (sorted descending)
  - Shows which domains AI search relies on — useful for planning
    where to earn coverage.
- Optional filter: `provider = perplexity`

## Tips

- Add a **date range control** and a **provider drop-down filter** to every
  page (Insert > Controls).
- Data freshness defaults to 12 hours for BigQuery sources. Adjust in the
  data source settings if you run scheduled prompts more often.
- Costs: Looker Studio issues BigQuery queries on view refresh. The
  `prompt_run_results` table is small in most deployments, but you can
  materialize views into tables later if needed.

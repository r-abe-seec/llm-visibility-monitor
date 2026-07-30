-- v0.4.0: Materialized dashboard tables.
-- Replace `your-project.your_dataset` with your GCP project ID and dataset.
--
-- The v_* views compute everything on the fly, including JSON parsing.
-- Once the prompt_run_results table grows, every dashboard refresh re-scans
-- and re-parses all rows. This script snapshots the views into partitioned,
-- clustered tables (t_*) that Looker Studio can query cheaply.
--
-- HOW TO USE:
--   Run manually once to create the tables, then register this script as a
--   BigQuery Scheduled Query (daily, after your prompt runs finish).
--   See docs/materialized-tables.md for step-by-step setup.

CREATE OR REPLACE TABLE `your-project.your_dataset.t_visibility_daily`
PARTITION BY run_date
CLUSTER BY provider
AS
SELECT * FROM `your-project.your_dataset.v_visibility_daily`;

CREATE OR REPLACE TABLE `your-project.your_dataset.t_brand_mentions`
PARTITION BY run_date
CLUSTER BY brand, provider
AS
SELECT * FROM `your-project.your_dataset.v_brand_mentions`;

CREATE OR REPLACE TABLE `your-project.your_dataset.t_citations`
PARTITION BY run_date
CLUSTER BY citation_domain
AS
SELECT * FROM `your-project.your_dataset.v_citations`;

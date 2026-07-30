-- v0.3.0: Analysis views for Looker Studio dashboards.
-- Replace `your-project.your_dataset` with your GCP project ID and dataset.
-- Requires the v0.2.0 migration (target_score / share_of_voice / citations /
-- analysis columns) to be applied first.

-- ---------------------------------------------------------------------------
-- 1. Daily visibility per provider (time-series trend)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW `your-project.your_dataset.v_visibility_daily` AS
SELECT
  DATE(executed_at, 'Asia/Tokyo') AS run_date,
  provider,
  COUNT(*) AS executions,
  AVG(target_score) AS avg_target_score,
  MAX(target_score) AS max_target_score,
  AVG(share_of_voice) AS avg_share_of_voice
FROM `your-project.your_dataset.prompt_run_results`
WHERE success
  AND target_score IS NOT NULL
GROUP BY run_date, provider;

-- ---------------------------------------------------------------------------
-- 2. Brand mentions flattened from the analysis JSON
--    (one row per brand per prompt execution; includes sentiment)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW `your-project.your_dataset.v_brand_mentions` AS
SELECT
  result_id,
  run_id,
  executed_at,
  DATE(executed_at, 'Asia/Tokyo') AS run_date,
  provider,
  model,
  prompt_id,
  JSON_VALUE(brand, '$.brand') AS brand,
  SAFE_CAST(JSON_VALUE(brand, '$.is_target') AS BOOL) AS is_target,
  SAFE_CAST(JSON_VALUE(brand, '$.mentioned') AS BOOL) AS mentioned,
  SAFE_CAST(JSON_VALUE(brand, '$.count') AS INT64) AS mention_count,
  SAFE_CAST(JSON_VALUE(brand, '$.rank') AS INT64) AS rank,
  SAFE_CAST(JSON_VALUE(brand, '$.visibility_score') AS FLOAT64)
    AS visibility_score,
  JSON_VALUE(brand, '$.sentiment') AS sentiment
FROM `your-project.your_dataset.prompt_run_results`,
UNNEST(JSON_EXTRACT_ARRAY(analysis, '$.brands')) AS brand
WHERE success
  AND analysis IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 3. Citations flattened (which sources AI search cites; Perplexity etc.)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW `your-project.your_dataset.v_citations` AS
SELECT
  result_id,
  run_id,
  executed_at,
  DATE(executed_at, 'Asia/Tokyo') AS run_date,
  provider,
  prompt_id,
  JSON_VALUE(citation) AS citation_url,
  NET.REG_DOMAIN(JSON_VALUE(citation)) AS citation_domain
FROM `your-project.your_dataset.prompt_run_results`,
UNNEST(JSON_EXTRACT_ARRAY(citations)) AS citation
WHERE success
  AND citations IS NOT NULL
  AND citations != '[]';

# Cloud Run Deployment Guide

Deploy LLM Visibility Monitor to Google Cloud Run so it runs continuously —
including the built-in scheduler for daily prompt runs.

## Prerequisites

- A GCP project with billing enabled
- `gcloud` CLI installed and authenticated (`gcloud auth login`)
- BigQuery dataset and table prepared (see `docs/bigquery-schema.md` and
  `sql/migrations/`)

## 1. Enable required APIs

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

## 2. Create a service account

Cloud Run should run with a dedicated service account that can write to
BigQuery.

```bash
gcloud iam service-accounts create lvm-runner --display-name "LLM Visibility Monitor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:lvm-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member "serviceAccount:lvm-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/bigquery.jobUser"
```

On Cloud Run, the BigQuery client authenticates automatically via this
service account — no key file is needed.

## 3. Build and push the image

```bash
gcloud artifacts repositories create lvm --repository-format=docker --location=asia-northeast1

gcloud builds submit --tag asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/lvm/llm-visibility-monitor:latest
```

## 4. Deploy

```bash
gcloud run deploy llm-visibility-monitor \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/lvm/llm-visibility-monitor:latest \
  --region asia-northeast1 \
  --service-account lvm-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  --min-instances 1 \
  --no-cpu-throttling \
  --set-env-vars "RESULT_REPOSITORY=bigquery,GCP_PROJECT_ID=YOUR_PROJECT_ID,BIGQUERY_DATASET=your_dataset,SCHEDULE_ENABLED=true,SCHEDULE_CRON=0 6 * * *,SCHEDULE_TIMEZONE=Asia/Tokyo,SCHEDULE_PROVIDERS=openai" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

Store API keys in Secret Manager rather than plain env vars:

```bash
echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
```

Repeat for `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `PERPLEXITY_API_KEY`,
and Azure settings as needed.

## Important flags for the scheduler

Two flags are required for the built-in scheduler to fire reliably:

| Flag | Why |
|------|-----|
| `--min-instances 1` | Cloud Run scales to zero by default; a scaled-down instance cannot run scheduled jobs. |
| `--no-cpu-throttling` | By default CPU is only allocated during request handling; the scheduler runs outside requests and needs always-on CPU. |

Note: both flags mean the instance is billed continuously. If you prefer
scale-to-zero pricing, disable the built-in scheduler
(`SCHEDULE_ENABLED=false`) and use **Cloud Scheduler** to POST to `/runs`
on a cron schedule instead:

```bash
gcloud scheduler jobs create http lvm-daily-run \
  --location asia-northeast1 \
  --schedule "0 6 * * *" \
  --time-zone "Asia/Tokyo" \
  --uri "https://YOUR_SERVICE_URL/runs" \
  --http-method POST \
  --headers "Content-Type=application/json" \
  --message-body '{"provider": "openai", "prompt_ids": ["recommend_ad_agencies", "recommend_ga4_agencies"]}' \
  --oidc-service-account-email lvm-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 5. Verify

```bash
gcloud run services describe llm-visibility-monitor --region asia-northeast1 --format "value(status.url)"
```

Then check `GET /health` and `GET /schedule` on the service URL
(use `gcloud run services proxy` for authenticated access during testing).

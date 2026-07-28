# LLM Visibility Monitor

An open-source platform for measuring and monitoring brand visibility across large language models (LLMs).

## Features

- Monitor brand mentions in ChatGPT
- Measure citation rates and source domains
- Compare visibility across ChatGPT, Gemini, Claude, and Perplexity
- Store historical data in BigQuery
- Visualize trends with Looker Studio
- Deploy on Google Cloud Run

## Architecture

Cloud Scheduler
      │
      ▼
Cloud Run
      │
      ▼
OpenAI / Gemini / Claude APIs
      │
      ▼
BigQuery
      │
      ▼
Looker Studio
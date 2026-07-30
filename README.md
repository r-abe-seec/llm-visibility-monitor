# LLM Visibility Monitor

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An open-source platform for evaluating and monitoring brand visibility across Large Language Models (LLMs).

LLM Visibility Monitor provides an API-first framework for executing prompts against multiple LLM providers and storing execution results in configurable repositories for later analysis.

The project aims to help marketers, SEO professionals, and developers measure how brands appear in AI-generated responses over time.

## Features

- Execute prompts against multiple LLM providers
- Execute multiple prompts in a single request
- Support OpenAI and Anthropic providers
- Configurable result repositories
  - Console
  - JSON
  - BigQuery
- Store execution results in BigQuery
- FastAPI REST API
- Environment-based configuration

## Architecture

```text
                +----------------+
                |    FastAPI     |
                +-------+--------+
                        |
                        v
            +----------------------+
            | BatchPromptRunner    |
            +----------+-----------+
                       |
        +--------------+--------------+
        |                             |
        v                             v
+---------------+          +----------------------+
| LLM Providers |          | Result Repository    |
+---------------+          +----------------------+
| OpenAI        |          | Console              |
| Anthropic     |          | JSON                 |
+---------------+          | BigQuery             |
                           +----------------------+
```

## Quick Start

Clone the repository.

```bash
git clone https://github.com/r-abe-seec/llm-visibility-monitor.git
cd llm-visibility-monitor
```

Create and activate a virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update the required environment variables.

Run the API.

```bash
uvicorn src.main:app --reload
```

Open Swagger UI.

```text
http://localhost:8000/docs
```

## Configuration

Example `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

RESULT_REPOSITORY=bigquery

GCP_PROJECT_ID=your-gcp-project
BIGQUERY_DATASET=llm_visibility
BIGQUERY_TABLE=prompt_run_results
```

Supported values for `RESULT_REPOSITORY`:

- `console`
- `json`
- `bigquery`

## BigQuery Setup

Authenticate with Application Default Credentials.

```bash
gcloud auth application-default login
```

Create the BigQuery table using the schema in:

```text
docs/bigquery-schema.md
```

## Roadmap

### Completed

- [x] FastAPI REST API
- [x] OpenAI provider
- [x] Anthropic provider
- [x] BigQuery repository

### Planned

- [ ] Unit tests
- [ ] GitHub Actions (CI)
- [ ] Gemini provider
- [ ] Perplexity provider
- [ ] Result history API
- [ ] Looker Studio dashboard
- [ ] Cloud Run deployment guide

## Contributing

Contributions are welcome.

If you find a bug or have a feature request, please open an issue before submitting a pull request.

## License

This project is licensed under the MIT License.
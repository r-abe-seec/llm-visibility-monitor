# LLM Visibility Monitor
![CI](https://github.com/r-abe-seec/llm-visibility-monitor/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An open-source platform for evaluating and monitoring brand visibility across Large Language Models (LLMs).

LLM Visibility Monitor provides an API-first framework for executing prompts against multiple LLM providers and storing execution results in configurable repositories for later analysis.

The project helps marketers, SEO professionals, and developers measure how brands appear in AI-generated responses over time.

---

## Features

- Execute prompts against multiple LLM providers
- Execute multiple prompts in a single request
- Support OpenAI, Anthropic, Gemini, and Perplexity providers
- Configurable result repositories
  - Console
  - JSON
  - BigQuery
- Store execution results in BigQuery
- Brand visibility analysis (mention detection, ranking, visibility score, share of voice)
- Sentiment analysis of brand mentions (judged by the executing LLM)
- Result history API (past runs and brand visibility over time)
- Scheduled daily runs (built-in cron scheduler, opt-in)
- Competitive comparison report (target vs competitor visibility)
- FastAPI REST API
- Docker & Docker Compose support
- Environment-based configuration

---

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
| Gemini        |          | BigQuery             |
| Perplexity    |          |                      |
+---------------+          +----------------------+
       |
       v
+----------------------+
| Visibility Analysis  |
+----------------------+
| Mention detection    |
| Ranking              |
| Visibility scoring   |
+----------------------+
```

---

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

Copy `.env.example` to `.env`.

Start the application.

```bash
uvicorn src.main:app --reload
```

Open Swagger UI.

```text
http://localhost:8000/docs
```

---

## Docker

### Docker Compose (Recommended)

Build and start the application.

```bash
docker compose up --build
```

Run in detached mode.

```bash
docker compose up --build -d
```

Check container status.

```bash
docker compose ps
```

View logs.

```bash
docker compose logs -f app
```

Open Swagger UI.

```text
http://localhost:8000/docs
```

Stop the application.

```bash
docker compose down
```

---

### Docker CLI

Build the image.

```bash
docker build -t llm-visibility-monitor .
```

Run the container.

```bash
docker run --rm -p 8000:8000 --env-file .env llm-visibility-monitor
```

---

## Configuration

Example `.env`

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

RESULT_REPOSITORY=console

GCP_PROJECT_ID=your-gcp-project
BIGQUERY_DATASET=llm_visibility
BIGQUERY_TABLE=prompt_run_results
```

Supported values for `RESULT_REPOSITORY`

- `console`
- `json`
- `bigquery`

---

## BigQuery Setup

Authenticate with Application Default Credentials.

```bash
gcloud auth application-default login
```

Create the BigQuery table using the schema located in

```text
docs/bigquery-schema.md
```

When running inside Docker, mount your Google Cloud credentials and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

Never commit credentials or service account keys to Git.

---

## Development

Run tests.

```bash
pytest
```

Run Ruff.

```bash
ruff check .
ruff format .
```

Run mypy.

```bash
mypy src
```

---

## Quality

This project uses:

- pytest
- Ruff
- mypy
- GitHub Actions
- Docker
- Docker Compose

---

## Roadmap

### Completed

- ✅ FastAPI REST API
- ✅ OpenAI provider
- ✅ Anthropic provider
- ✅ BigQuery repository
- ✅ Unit tests
- ✅ GitHub Actions
- ✅ Ruff
- ✅ mypy
- ✅ Docker
- ✅ Docker Compose
- ✅ Gemini provider
- ✅ Perplexity provider
- ✅ Result history API
- ✅ Competitive comparison report
- ✅ Sentiment analysis
- ✅ Scheduled runs

### Planned

- Azure OpenAI provider
- Looker Studio dashboard
- Cloud Run deployment guide

---

## Contributing

Contributions are welcome.

Please open an Issue before submitting a Pull Request for significant changes.

---

## License

This project is licensed under the MIT License.
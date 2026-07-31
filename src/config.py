from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "LLM Visibility Monitor"
    version: str = "0.2.0"

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    # Anthropic
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Azure OpenAI
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str | None = None

    # Perplexity (OpenAI-compatible API)
    perplexity_api_key: str | None = None
    perplexity_model: str = "sonar"
    perplexity_base_url: str = "https://api.perplexity.ai"

    # BigQuery
    gcp_project_id: str | None = None
    bigquery_dataset: str | None = None
    bigquery_table: str = "prompt_run_results"

    result_repository: str = "json"
    results_dir: str = "data/results"
    history_max_runs: int = 100

    # Scheduled runs (disabled by default to avoid unexpected API cost)
    schedule_enabled: bool = False
    schedule_cron: str = "0 6 * * *"
    schedule_timezone: str = "Asia/Tokyo"
    schedule_providers: str = "openai"
    schedule_prompt_ids: str = ""

    # Alerts (disabled by default)
    alert_enabled: bool = False
    alert_score_drop_threshold: float = 20.0
    slack_webhook_url: str | None = None
    google_chat_webhook_url: str | None = None

    # Visibility analysis
    analysis_enabled: bool = True
    sentiment_enabled: bool = True
    brands_file: str = "prompts/brands.yaml"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

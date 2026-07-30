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

    # BigQuery
    gcp_project_id: str | None = None
    bigquery_dataset: str | None = None
    bigquery_table: str = "prompt_run_results"

    result_repository: str = "json"

    # Visibility analysis
    analysis_enabled: bool = True
    brands_file: str = "prompts/brands.yaml"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

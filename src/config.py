from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "LLM Visibility Monitor"
    version: str = "0.1.0"

    openai_api_key: str | None = None
    openai_model: str | None = None

    anthropic_api_key: str | None = None
    anthropic_model: str | None = None

    gcp_project_id: str | None = None
    bigquery_dataset: str | None = None
    bigquery_table: str = "prompt_run_results"

    result_repository: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
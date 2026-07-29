from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "LLM Visibility Monitor"
    version: str = "0.1.0"


settings = Settings()
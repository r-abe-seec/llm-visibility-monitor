from fastapi import FastAPI, HTTPException

from src.config import settings
from src.services.llm.factory import ProviderFactory

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "project": settings.project_name,
        "version": settings.version,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/hello/{provider_name}")
def hello(provider_name: str):
    try:
        provider = ProviderFactory.create(provider_name)

        result = provider.generate(
            "日本語で短く挨拶してください。"
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
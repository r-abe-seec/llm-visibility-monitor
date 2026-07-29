from fastapi import FastAPI

from src.config import settings

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
    return {
        "status": "healthy"
    }
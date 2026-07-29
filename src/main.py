from fastapi import FastAPI

app = FastAPI(
    title="LLM Visibility Monitor",
    version="0.1.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "project": "LLM Visibility Monitor",
        "version": "0.1.0",
    }
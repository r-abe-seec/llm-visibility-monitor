from fastapi import FastAPI, HTTPException

from src.application.batch_prompt_runner import BatchPromptRunner
from src.config import settings
from src.models.prompt_run import PromptRunRequest, PromptRunResult
from src.factories.repository_factory import RepositoryFactory
from src.services.llm.factory import ProviderFactory
from src.services.prompt_service import PromptService


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)

prompt_service = PromptService()
result_repository = RepositoryFactory.create("json")

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


@app.get("/prompts")
def list_prompts():
    return prompt_service.load_all()


@app.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: str):
    try:
        return prompt_service.get(prompt_id)

    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@app.get("/run/{provider_name}/{prompt_id}")
def run_prompt(provider_name: str, prompt_id: str):
    try:
        prompt = prompt_service.get(prompt_id)
        provider = ProviderFactory.create(provider_name)

        return provider.generate(prompt.text)

    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.post("/runs", response_model=PromptRunResult)
def run_prompts(request: PromptRunRequest) -> PromptRunResult:
    try:
        runner = BatchPromptRunner(
            prompt_service=prompt_service,
            result_repository=result_repository,
        )

        return runner.run(
            provider_name=request.provider,
            prompt_ids=request.prompt_ids,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
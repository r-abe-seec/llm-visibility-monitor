from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.models.prompt import Prompt
from src.services.prompt_generator import PromptGenerator
from src.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["prompts"])


def get_generator() -> PromptGenerator:
    return PromptGenerator()


def get_prompt_service() -> PromptService:
    return PromptService()


GeneratorDep = Annotated[PromptGenerator, Depends(get_generator)]
PromptServiceDep = Annotated[PromptService, Depends(get_prompt_service)]


class GeneratePromptsRequest(BaseModel):
    industry: str = Field(min_length=1)
    target: str | None = None
    categories: list[str] | None = None
    save: bool = False


class GeneratePromptsResponse(BaseModel):
    generated: list[Prompt]
    saved: bool


@router.post("/generate", response_model=GeneratePromptsResponse)
def generate_prompts(
    request: GeneratePromptsRequest,
    generator: GeneratorDep,
    prompt_service: PromptServiceDep,
) -> GeneratePromptsResponse:
    try:
        existing_ids = {prompt.id for prompt in prompt_service.load_all()}
    except FileNotFoundError:
        existing_ids = set()

    prompts = generator.generate(
        industry=request.industry,
        target=request.target,
        categories=request.categories,
        existing_ids=existing_ids,
    )

    if request.save and prompts:
        prompt_service.append(prompts)

    return GeneratePromptsResponse(
        generated=prompts,
        saved=request.save and bool(prompts),
    )

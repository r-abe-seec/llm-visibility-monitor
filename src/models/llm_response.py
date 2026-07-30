from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    provider: str
    model: str
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    citations: list[str] = Field(default_factory=list)

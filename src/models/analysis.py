from pydantic import BaseModel


class BrandMention(BaseModel):
    brand: str
    is_target: bool
    mentioned: bool
    count: int
    first_position: int | None = None
    rank: int | None = None
    visibility_score: float
    sentiment: str | None = None


class VisibilityAnalysis(BaseModel):
    brands: list[BrandMention]
    target_score: float
    share_of_voice: float

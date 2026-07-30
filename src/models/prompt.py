from pydantic import BaseModel, Field


class Prompt(BaseModel):
    id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)

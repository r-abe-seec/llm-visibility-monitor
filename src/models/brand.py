from pydantic import BaseModel, Field


class Brand(BaseModel):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    is_target: bool = False

    def terms(self) -> list[str]:
        """Name plus aliases, used for matching."""
        return [self.name, *self.aliases]

from pydantic import BaseModel


class LoadedSkill(BaseModel):
    instructions: str
    references: dict[str, str]


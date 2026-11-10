
from pydantic import BaseModel, Field, ConfigDict


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=500)
    default_language: str = Field(min_length=1, max_length=50)


class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    default_language: str

    model_config = ConfigDict(from_attributes=True)

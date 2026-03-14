from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)


class RetrieveResponse(BaseModel):
    results: list[dict[str, str]] = Field(default_factory=list)

from pydantic import BaseModel, Field

from models.knowledge import RetrievedKnowledgeChunk


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)


class RetrieveResponse(BaseModel):
    results: list[RetrievedKnowledgeChunk] = Field(default_factory=list)
    retrieval_query: str | None = None

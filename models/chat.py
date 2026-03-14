from pydantic import BaseModel, Field

from models.common import ConversationMessage
from models.knowledge import RetrievedKnowledgeChunk


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    context: list[ConversationMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    verses: list[RetrievedKnowledgeChunk] = Field(default_factory=list)
    retrieval_query: str | None = None

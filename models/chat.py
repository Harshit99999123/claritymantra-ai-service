from pydantic import BaseModel, Field

from models.common import ConversationMessage


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    context: list[ConversationMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    verses: list[dict[str, str]] = Field(default_factory=list)

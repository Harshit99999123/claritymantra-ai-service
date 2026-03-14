from pydantic import BaseModel, Field

from models.common import ConversationMessage


class InsightRequest(BaseModel):
    conversation: list[ConversationMessage] = Field(default_factory=list)


class InsightResponse(BaseModel):
    quote: str
    meaning: str
    reflection: str
    shloka: str | None = None

from pydantic import BaseModel, Field

from models.common import ConversationMessage


class ChatVerse(BaseModel):
    reference: str
    translation: str
    themes: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    context: list[ConversationMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reflection: str
    reflection_question: str
    verses: list[ChatVerse] = Field(default_factory=list)

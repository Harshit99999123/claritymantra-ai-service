from pydantic import BaseModel, Field


class KnowledgeSource(BaseModel):
    slug: str
    title: str
    kind: str = "book"


class KnowledgeChunk(BaseModel):
    chunk_id: str
    source: KnowledgeSource
    reference: str
    chapter: int | None = None
    verse: int | None = None
    verse_label: str | None = None
    original_text: str = ""
    translation: str
    interpretation: str
    themes: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)

    @property
    def embedding_text(self) -> str:
        return " ".join(
            [
                self.translation,
                self.interpretation,
                " ".join(self.themes),
                " ".join(self.emotions),
            ]
        ).strip()


class RetrievedKnowledgeChunk(BaseModel):
    chunk_id: str
    source: KnowledgeSource
    reference: str
    chapter: int | None = None
    verse: int | None = None
    verse_label: str | None = None
    translation: str
    interpretation: str
    themes: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    retrieval_score: float
    retrieval_reason: str

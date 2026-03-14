from dataclasses import dataclass

from models.knowledge import KnowledgeChunk


@dataclass
class IndexedChunk:
    chunk: KnowledgeChunk
    embedding: list[float]
    semantic_text: str

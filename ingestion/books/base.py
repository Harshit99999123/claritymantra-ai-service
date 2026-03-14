from abc import ABC, abstractmethod

from ingestion.models import BookDefinition
from models.knowledge import KnowledgeChunk


class BookIngestor(ABC):
    @abstractmethod
    def ingest(self, definition: BookDefinition) -> list[KnowledgeChunk]:
        raise NotImplementedError

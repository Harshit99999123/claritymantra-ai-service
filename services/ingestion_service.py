import json
from datetime import datetime, UTC
from pathlib import Path

from core.logging import get_logger
from ingestion.factory import build_ingestor
from ingestion.models import IngestionBookResponse, IngestionRunResponse
from ingestion.registry import get_book_definition, list_books
from models.knowledge import KnowledgeChunk


class IngestionService:
    def __init__(self, settings, vector_store, embeddings) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.logger = get_logger(__name__)

    def list_books(self) -> list[IngestionBookResponse]:
        return [
            IngestionBookResponse(
                slug=book.slug,
                title=book.title,
                source_kind=book.source_kind,
                source_document_path=book.source_document_path,
                output_dataset_path=book.output_dataset_path,
                active_for_retrieval=book.slug == self.settings.active_book_slug,
            )
            for book in list_books()
        ]

    async def run_ingestion(self, book_slug: str, refresh_active_index: bool = True) -> IngestionRunResponse:
        definition = get_book_definition(book_slug)
        ingestor = build_ingestor(definition)
        chunks = ingestor.ingest(definition)
        self._write_outputs(definition.output_dataset_path, definition.output_metadata_path, definition, chunks)

        refreshed = False
        if refresh_active_index and definition.slug == self.settings.active_book_slug:
            await self.vector_store.index(chunks, self.embeddings)
            self.vector_store.write_manifest(
                {
                    "collection_name": self.vector_store.collection_name,
                    "embedding_provider": self.settings.embedding_provider,
                    "embedding_model": self.settings.embedding_model,
                    "record_count": len(chunks),
                    "active_book_slug": self.settings.active_book_slug,
                }
            )
            refreshed = True

        self.logger.info("ingestion.completed book=%s records=%s refreshed=%s", book_slug, len(chunks), refreshed)
        return IngestionRunResponse(
            book_slug=definition.slug,
            title=definition.title,
            output_dataset_path=definition.output_dataset_path,
            output_metadata_path=definition.output_metadata_path,
            records_written=len(chunks),
            refreshed_active_index=refreshed,
        )

    def _write_outputs(
        self,
        dataset_path: str,
        metadata_path: str,
        definition,
        chunks: list[KnowledgeChunk],
    ) -> None:
        dataset_file = Path(dataset_path)
        metadata_file = Path(metadata_path)
        dataset_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)

        dataset_file.write_text(
            json.dumps([chunk.model_dump() for chunk in chunks], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        metadata_file.write_text(
            json.dumps(
                {
                    "book_slug": definition.slug,
                    "title": definition.title,
                    "source_document_path": definition.source_document_path,
                    "structured_source_path": definition.structured_source_path,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "records_written": len(chunks),
                    "refresh_active_index": definition.slug == self.settings.active_book_slug,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

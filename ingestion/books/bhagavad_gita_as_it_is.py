import json
from pathlib import Path

from ingestion.books.base import BookIngestor
from ingestion.books.bhagavad_gita_parser import parse_bhagavad_gita_pdf
from ingestion.models import BookDefinition
from models.knowledge import KnowledgeChunk


class BhagavadGitaAsItIsIngestor(BookIngestor):
    def ingest(self, definition: BookDefinition) -> list[KnowledgeChunk]:
        parsed_chunks = parse_bhagavad_gita_pdf(
            pdf_path=definition.source_document_path,
            source_slug=definition.slug,
            source_title=definition.title,
            source_kind=definition.source_kind,
        )
        seed_path = Path(definition.structured_source_path)
        if not seed_path.exists():
            return parsed_chunks

        overrides = {
            record["chunk_id"]: record
            for record in json.loads(seed_path.read_text(encoding="utf-8"))
        }
        merged: list[KnowledgeChunk] = []
        for chunk in parsed_chunks:
            override = overrides.get(chunk.chunk_id)
            if override:
                normalized_override = dict(override)
                if "interpretation" not in normalized_override and "meaning" in normalized_override:
                    normalized_override["interpretation"] = normalized_override["meaning"]
                merged.append(KnowledgeChunk(**{**chunk.model_dump(), **normalized_override}))
            else:
                merged.append(chunk)
        return merged

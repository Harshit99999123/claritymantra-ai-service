import json
from pathlib import Path

from models.knowledge import KnowledgeChunk, KnowledgeSource


def load_dataset(dataset_path: str, source_slug: str, source_title: str, source_kind: str) -> list[KnowledgeChunk]:
    path = Path(dataset_path)
    records = json.loads(path.read_text(encoding="utf-8"))
    normalized = [
        normalize_record(
            record=record,
            source_slug=source_slug,
            source_title=source_title,
            source_kind=source_kind,
        )
        for record in records
    ]
    return [KnowledgeChunk(**record) for record in normalized]


def normalize_record(record: dict[str, object], source_slug: str, source_title: str, source_kind: str) -> dict[str, object]:
    normalized = dict(record)
    if "interpretation" not in normalized and "meaning" in normalized:
        normalized["interpretation"] = normalized["meaning"]
    if "source" not in normalized:
        normalized["source"] = KnowledgeSource(
            slug=source_slug,
            title=source_title,
            kind=source_kind,
        ).model_dump()
    if "reference" not in normalized:
        chapter = normalized.get("chapter")
        verse_label = normalized.get("verse_label")
        verse = normalized.get("verse")
        if chapter is not None and (verse_label is not None or verse is not None):
            normalized["reference"] = f"{chapter}.{verse_label or verse}"
        else:
            normalized["reference"] = str(normalized.get("chunk_id", "unknown"))
    return normalized

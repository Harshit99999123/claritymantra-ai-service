from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.logging import get_logger
from models.knowledge import KnowledgeChunk, KnowledgeSource, RetrievedKnowledgeChunk
from rag.indexer import IndexedChunk
from rag.query_expansion import expand_query_terms, tokenize


@dataclass
class RetrievalScore:
    chunk: KnowledgeChunk
    score: float
    reason: str


class ChromaVectorStore:
    def __init__(self, persist_path: str, collection_name: str = "knowledge_chunks") -> None:
        self.persist_path = Path(persist_path)
        self.collection_name = collection_name
        self.logger = get_logger(__name__)
        self._documents: list[IndexedChunk] = []
        self._client = None
        self._collection = None

    async def index(self, chunks: list[KnowledgeChunk], embeddings) -> None:
        self._reset_collection()
        self._documents = []

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, object]] = []
        vectors: list[list[float]] = []

        for chunk in chunks:
            semantic_text = chunk.embedding_text
            embedding = await embeddings.embed(semantic_text)
            self._documents.append(IndexedChunk(chunk=chunk, embedding=embedding, semantic_text=semantic_text))
            ids.append(chunk.chunk_id)
            documents.append(semantic_text)
            metadatas.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "source_slug": chunk.source.slug,
                    "source_title": chunk.source.title,
                    "source_kind": chunk.source.kind,
                    "reference": chunk.reference,
                    "chapter": chunk.chapter,
                    "verse": chunk.verse or 0,
                    "verse_label": chunk.verse_label or "",
                    "translation": chunk.translation,
                    "interpretation": chunk.interpretation,
                    "themes": "|".join(chunk.themes),
                    "emotions": "|".join(chunk.emotions),
                }
            )
            vectors.append(embedding)

        collection = self._get_collection()
        batch_size = 128
        for index in range(0, len(ids), batch_size):
            collection.add(
                ids=ids[index:index + batch_size],
                documents=documents[index:index + batch_size],
                metadatas=metadatas[index:index + batch_size],
                embeddings=vectors[index:index + batch_size],
            )
        self.logger.info("vector_store.indexed provider=chroma records=%s", len(ids))

    async def search(self, query: str, embedding: list[float], top_k: int = 5, candidate_pool: int = 20) -> list[RetrievedKnowledgeChunk]:
        collection = self._get_collection()
        chroma_results = collection.query(
            query_embeddings=[embedding],
            n_results=min(max(top_k, candidate_pool), max(1, collection.count())),
            include=["metadatas", "documents", "distances"],
        )

        metadatas = chroma_results.get("metadatas", [[]])[0]
        documents = chroma_results.get("documents", [[]])[0]
        distances = chroma_results.get("distances", [[]])[0]

        candidates: list[IndexedChunk] = []
        for metadata, document, _distance in zip(metadatas, documents, distances):
            chunk = KnowledgeChunk(
                chunk_id=str(metadata["chunk_id"]),
                source=KnowledgeSource(
                    slug=str(metadata["source_slug"]),
                    title=str(metadata["source_title"]),
                    kind=str(metadata.get("source_kind") or "book"),
                ),
                reference=str(metadata["reference"]),
                chapter=int(metadata["chapter"]) or None,
                verse=int(metadata["verse"]) or None,
                verse_label=str(metadata.get("verse_label") or "") or None,
                translation=str(metadata["translation"]),
                interpretation=str(metadata["interpretation"]),
                themes=split_tag_field(metadata.get("themes")),
                emotions=split_tag_field(metadata.get("emotions")),
            )
            candidates.append(IndexedChunk(chunk=chunk, embedding=[], semantic_text=str(document)))

        query_terms = expand_query_terms(query)
        scored: list[RetrievalScore] = []
        for candidate, distance in zip(candidates, distances):
            lexical_terms = tokenize(candidate.semantic_text)
            theme_overlap = len(query_terms & set(candidate.chunk.themes))
            emotion_overlap = len(query_terms & set(candidate.chunk.emotions))
            lexical_overlap = len(query_terms & lexical_terms)
            semantic_score = 1.0 / (1.0 + float(distance))
            score = (
                semantic_score * 0.45
                + lexical_overlap * 0.15
                + theme_overlap * 0.25
                + emotion_overlap * 0.15
            )
            reason = build_reason(theme_overlap, emotion_overlap, lexical_overlap)
            scored.append(RetrievalScore(chunk=candidate.chunk, score=score, reason=reason))

        ranked = sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
        return [
            RetrievedKnowledgeChunk(
                chunk_id=item.chunk.chunk_id,
                source=item.chunk.source,
                reference=item.chunk.reference,
                chapter=item.chunk.chapter,
                verse=item.chunk.verse,
                verse_label=item.chunk.verse_label,
                translation=item.chunk.translation,
                interpretation=item.chunk.interpretation,
                themes=item.chunk.themes,
                emotions=item.chunk.emotions,
                retrieval_score=round(item.score, 4),
                retrieval_reason=item.reason,
            )
            for item in ranked
        ]

    def has_index(self) -> bool:
        try:
            return self._get_collection().count() > 0
        except Exception:
            return False

    def read_manifest(self) -> dict[str, object] | None:
        manifest_file = self._manifest_path()
        if not manifest_file.exists():
            return None
        return json.loads(manifest_file.read_text(encoding="utf-8"))

    def write_manifest(self, manifest: dict[str, object]) -> None:
        manifest_file = self._manifest_path()
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb  # type: ignore
                from chromadb.config import Settings as ChromaSettings  # type: ignore
            except ImportError as exc:
                raise RuntimeError("chromadb is not installed. Install requirements to use VECTOR_STORE_PROVIDER=chroma.") from exc
            self.persist_path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.persist_path),
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def _reset_collection(self) -> None:
        collection = self._collection
        client = self._client
        if client is None:
            collection = self._get_collection()
            client = self._client
        if client is not None:
            try:
                client.delete_collection(self.collection_name)
            except Exception:
                # Treat missing collections as a no-op during first index creation.
                pass
        self._collection = None

    def _manifest_path(self) -> Path:
        return self.persist_path / f"{self.collection_name}.manifest.json"


def split_tag_field(value: object) -> list[str]:
    if value is None:
        return []
    text = str(value)
    return [item for item in text.split("|") if item]


def build_reason(theme_overlap: int, emotion_overlap: int, lexical_overlap: int) -> str:
    reasons: list[str] = []
    if theme_overlap:
        reasons.append("theme match")
    if emotion_overlap:
        reasons.append("emotion match")
    if lexical_overlap:
        reasons.append("semantic overlap")
    return ", ".join(reasons) if reasons else "semantic similarity"

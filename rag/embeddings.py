from __future__ import annotations

import hashlib
from pathlib import Path

from core.logging import get_logger


class EmbeddingService:
    def __init__(self, provider: str, model_name: str) -> None:
        self.provider = provider
        self.model_name = model_name
        self.logger = get_logger(__name__)
        self._model = None

    async def embed(self, text: str) -> list[float]:
        if self.provider == "sentence-transformers":
            return self._embed_with_sentence_transformers(text)
        return self._embed_deterministically(text)

    def _embed_with_sentence_transformers(self, text: str) -> list[float]:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Either install it or set EMBEDDING_PROVIDER=deterministic."
                ) from exc
            model_source = self._resolve_sentence_transformer_source()
            self._model = SentenceTransformer(str(model_source), local_files_only=isinstance(model_source, Path))
            self.logger.info(
                "embeddings.loaded provider=sentence-transformers model=%s source=%s",
                self.model_name,
                str(model_source),
            )
        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def _resolve_sentence_transformer_source(self) -> str | Path:
        try:
            from huggingface_hub import snapshot_download  # type: ignore
        except ImportError:
            return self.model_name

        try:
            snapshot_path = snapshot_download(repo_id=self.model_name, local_files_only=True)
            resolved_path = Path(snapshot_path)
            if resolved_path.exists():
                self.logger.info(
                    "embeddings.using_cached_snapshot provider=sentence-transformers model=%s path=%s",
                    self.model_name,
                    resolved_path,
                )
                return resolved_path
        except Exception as exc:
            self.logger.warning(
                "embeddings.cached_snapshot_unavailable model=%s error=%s",
                self.model_name,
                exc,
            )

        self.logger.info(
            "embeddings.cached_snapshot_missing model=%s source=remote_identifier",
            self.model_name,
        )
        return self.model_name

    def _embed_deterministically(self, text: str) -> list[float]:
        buckets = [0.0] * 32
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % len(buckets)
            buckets[bucket] += 1.0
        norm = sum(value * value for value in buckets) ** 0.5 or 1.0
        return [value / norm for value in buckets]

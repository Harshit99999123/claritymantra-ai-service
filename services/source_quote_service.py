import json
import re
from pathlib import Path

from core.logging import get_logger
from models.knowledge import KnowledgeChunk


class SourceQuoteService:
    def __init__(self, llm_client, enabled: bool, cache_path: str) -> None:
        self.llm_client = llm_client
        self.enabled = enabled
        self.cache_path = Path(cache_path)
        self.logger = get_logger(__name__)

    async def format_chunks(self, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        if not chunks:
            return chunks

        cache = self._read_cache()
        formatted_chunks: list[KnowledgeChunk] = []

        for chunk in chunks:
            original_text = self._fallback_clean(chunk.original_text)
            if not original_text:
                formatted_chunks.append(chunk.model_copy(update={"original_text": ""}))
                continue

            cache_key = f"{chunk.source.slug}:{chunk.reference}:{original_text}"
            formatted = cache.get(cache_key)

            if formatted is None and self.enabled:
                try:
                    formatted = await self.llm_client.format_source_quote(
                        source_text=original_text,
                        reference=chunk.reference,
                        source_title=chunk.source.title,
                    )
                except Exception:
                    formatted = ""

            final_text = self._fallback_clean(formatted or original_text)
            cache[cache_key] = final_text
            formatted_chunks.append(chunk.model_copy(update={"original_text": final_text}))

        self._write_cache(cache)
        self.logger.info("source_quote.format_chunks formatted=%s enabled=%s", len(formatted_chunks), self.enabled)
        return formatted_chunks

    def _read_cache(self) -> dict[str, str]:
        if not self.cache_path.exists():
            return {}
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_cache(self, cache: dict[str, str]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _fallback_clean(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", (text or "").replace("\n", " ")).strip()
        cleaned = re.sub(r"\)\)\s*\d+\s*\)\)", "", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        if any(token in cleaned for token in ("[", "]", "<", ">", "\\", "_", "*", "=")):
            return ""
        if len(cleaned.split()) < 2:
            return ""
        return cleaned

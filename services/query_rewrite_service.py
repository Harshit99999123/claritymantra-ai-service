from __future__ import annotations

import re

from core.logging import get_logger


COMMON_REPLACEMENTS = {
    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "im": "i'm",
    "ive": "i've",
    "idk": "I don't know",
    "dnt": "don't",
    "knw": "know",
    "coz": "because",
    "bcoz": "because",
    "wht": "what",
    "abt": "about",
    "smth": "something",
    "tht": "that",
    "evrything": "everything",
    "rn": "right now",
}


class QueryRewriteService:
    def __init__(self, llm_client, enabled: bool) -> None:
        self.llm_client = llm_client
        self.enabled = enabled
        self.logger = get_logger(__name__)

    async def rewrite(self, query: str) -> str:
        fallback = self._fallback_rewrite(query)
        if not self.enabled:
            return fallback

        try:
            rewritten = await self.llm_client.rewrite_query(query=query)
        except Exception as exc:
            self.logger.warning("query_rewrite.failed error=%s", exc)
            return fallback

        cleaned = self._finalize(rewritten, fallback)
        self.logger.info(
            "query_rewrite.completed original_length=%s rewritten_length=%s changed=%s",
            len(query),
            len(cleaned),
            cleaned != query.strip(),
        )
        return cleaned

    def _fallback_rewrite(self, query: str) -> str:
        normalized = query.strip()
        normalized = re.sub(r"\s+", " ", normalized)
        words = []
        for raw_word in normalized.split():
            trailing = ""
            if raw_word and raw_word[-1] in ".,!?":
                trailing = raw_word[-1]
                raw_word = raw_word[:-1]
            replacement = COMMON_REPLACEMENTS.get(raw_word.lower(), raw_word)
            words.append(f"{replacement}{trailing}")
        rewritten = " ".join(words).strip()
        rewritten = rewritten.replace(" is mess", " is a mess")
        if rewritten and rewritten[-1] not in ".!?":
            rewritten = f"{rewritten}."
        if rewritten:
            rewritten = rewritten[0].upper() + rewritten[1:]
        return rewritten or query.strip()

    def _finalize(self, rewritten: str, fallback: str) -> str:
        cleaned = re.sub(r"\s+", " ", rewritten).strip()
        cleaned = cleaned.strip('"').strip("'")
        return cleaned or fallback

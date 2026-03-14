import json
from collections.abc import AsyncIterator

import httpx

from llm.prompt_builder import build_chat_prompt, build_query_rewrite_prompt


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model_name: str,
        query_rewrite_model: str,
        keep_alive: str,
        chat_temperature: float,
        chat_max_tokens: int,
        query_rewrite_max_tokens: int,
    ) -> None:
        self.base_url = base_url
        self.model_name = model_name
        self.query_rewrite_model = query_rewrite_model
        self.keep_alive = keep_alive
        self.chat_temperature = chat_temperature
        self.chat_max_tokens = chat_max_tokens
        self.query_rewrite_max_tokens = query_rewrite_max_tokens

    async def generate_chat_response(self, message: str, context, verses) -> str:
        prompt = build_chat_prompt(message=message, context=context, verses=verses)
        try:
            return await self._generate_text(prompt, max_tokens=self.chat_max_tokens, temperature=self.chat_temperature)
        except Exception:
            return self._fallback_chat_response(message=message, verses=verses)

    async def stream_chat_response(self, message: str, context, verses) -> AsyncIterator[str]:
        prompt = build_chat_prompt(message=message, context=context, verses=verses)
        try:
            async for token in self._stream_text(
                prompt,
                model_name=self.model_name,
                max_tokens=self.chat_max_tokens,
                temperature=self.chat_temperature,
            ):
                yield token
            return
        except Exception:
            pass

        fallback = self._fallback_chat_response(message=message, verses=verses)
        for token in self._chunk_text(fallback):
            yield token

    async def generate_insight(self, conversation, verses) -> dict[str, str]:
        verse = verses[0] if verses else None
        if verse is None:
            return {
                "quote": "Act with steadiness and clarity.",
                "meaning": "Focus on what is within your control.",
                "reflection": "What is one small step you can take with sincerity today?",
            }

        prompt = "\n\n".join(
            [
                "You are preparing a concise reflection card.",
                "Return valid JSON with keys: quote, meaning, reflection.",
                "Tone: calm, respectful, brief, modern, and non-preachy.",
                "Keep each field short and readable.",
                f"Source: {verse.source.title} {verse.reference}",
                f"Translation: {verse.translation}",
                f"Interpretation: {verse.interpretation}",
            ]
        )
        try:
            raw = await self._generate_text(prompt)
            return self._parse_insight_response(raw, verse)
        except Exception:
            return {
                "quote": verse.translation,
                "meaning": verse.interpretation,
                "reflection": "What part of this teaching feels most useful for your next step?",
            }

    async def rewrite_query(self, query: str) -> str:
        prompt = build_query_rewrite_prompt(query)
        rewritten = await self._generate_text(
            prompt,
            model_name=self.query_rewrite_model,
            max_tokens=self.query_rewrite_max_tokens,
            temperature=0.1,
        )
        return rewritten.splitlines()[0].strip()

    async def _generate_text(
        self,
        prompt: str,
        model_name: str | None = None,
        max_tokens: int = 220,
        temperature: float = 0.3,
    ) -> str:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            response = await client.post(
                "/api/generate",
                json={
                    "model": model_name or self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": self.keep_alive,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload.get("response", "")).strip()

    async def _stream_text(
        self,
        prompt: str,
        model_name: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            async with client.stream(
                "POST",
                "/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True,
                    "keep_alive": self.keep_alive,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "num_predict": max_tokens,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    payload = json.loads(line)
                    chunk = str(payload.get("response") or "")
                    if chunk:
                        yield chunk
                    if payload.get("done"):
                        break

    def _fallback_chat_response(self, message: str, verses) -> str:
        verse = verses[0] if verses else None
        if verse is None:
            return (
                "It sounds like this is weighing on you. "
                "Perhaps it may help to pause, notice what is within your control, "
                "and take one sincere next step. "
                "What feels most important for you to address first?"
            )
        return (
            "It sounds like this situation is carrying some weight for you. "
            f"A teaching from {verse.source.title} {verse.reference} may help here: "
            f"{verse.translation} "
            f"In modern terms, {verse.interpretation.lower()} "
            "You might consider choosing one honest action for today and letting the larger outcome unfold step by step."
        )

    def _parse_insight_response(self, raw: str, verse) -> dict[str, str]:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "quote": verse.translation,
                "meaning": verse.interpretation,
                "reflection": "What part of this teaching feels most useful for your next step?",
            }
        return {
            "quote": str(payload.get("quote") or verse.translation),
            "meaning": str(payload.get("meaning") or verse.interpretation),
            "reflection": str(
                payload.get("reflection")
                or "What part of this teaching feels most useful for your next step?"
            ),
        }

    def _chunk_text(self, text: str) -> list[str]:
        words = text.split()
        return [word + (" " if index < len(words) - 1 else "") for index, word in enumerate(words)]

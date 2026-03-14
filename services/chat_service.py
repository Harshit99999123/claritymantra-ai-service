from core.logging import get_logger
import re

from models.chat import ChatRequest, ChatResponse, ChatVerse
from models.retrieve import RetrieveResponse


class ChatService:
    def __init__(self, retriever, llm_client, query_rewrite_service) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.query_rewrite_service = query_rewrite_service
        self.logger = get_logger(__name__)

    async def generate_response(self, payload: ChatRequest) -> ChatResponse:
        retrieval_query = await self.query_rewrite_service.rewrite(payload.message)
        verses = await self.retriever.retrieve(retrieval_query, top_k=2)
        reflection_text = await self.llm_client.generate_chat_response(
            message=payload.message,
            context=payload.context,
            verses=verses,
        )
        reflection, question = self._split_reflection_text(reflection_text)
        self.logger.info("chat.generated_response verses=%s retrieval_query_changed=%s", len(verses), retrieval_query != payload.message)
        return ChatResponse(
            reflection=reflection,
            reflection_question=question,
            verses=[self._to_chat_verse(item) for item in verses],
        )

    async def stream_response(self, payload: ChatRequest):
        retrieval_query = await self.query_rewrite_service.rewrite(payload.message)
        verses = await self.retriever.retrieve(retrieval_query, top_k=2)
        self.logger.info("chat.stream_started verses=%s retrieval_query_changed=%s", len(verses), retrieval_query != payload.message)
        stream = self.llm_client.stream_chat_response(
            message=payload.message,
            context=payload.context,
            verses=verses,
        )
        return verses, stream

    async def retrieve_relevant_verses(self, query: str) -> RetrieveResponse:
        retrieval_query = await self.query_rewrite_service.rewrite(query)
        results = await self.retriever.retrieve(retrieval_query)
        return RetrieveResponse(results=results, retrieval_query=retrieval_query)

    def _split_reflection_text(self, text: str) -> tuple[str, str]:
        cleaned = text.strip()
        question = ""
        for line in reversed(cleaned.splitlines()):
            candidate = line.strip()
            if candidate.endswith("?"):
                question = candidate
                break
        if not question:
            sentences = [sent.strip() for sent in re.split(r"(?<=[?])\s+", cleaned) if sent.strip()]
            question = sentences[-1] if sentences else ""
        if not question:
            question = "What feels like the most meaningful next step for you?"
        return cleaned, question

    def _to_chat_verse(self, verse) -> ChatVerse:
        return ChatVerse(
            reference=verse.reference,
            translation=verse.translation,
            themes=verse.themes,
        )

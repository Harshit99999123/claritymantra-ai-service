from core.logging import get_logger
from models.chat import ChatRequest, ChatResponse
from models.retrieve import RetrieveResponse


class ChatService:
    def __init__(self, retriever, llm_client, query_rewrite_service) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.query_rewrite_service = query_rewrite_service
        self.logger = get_logger(__name__)

    async def generate_response(self, payload: ChatRequest) -> ChatResponse:
        retrieval_query = await self.query_rewrite_service.rewrite(payload.message)
        verses = await self.retriever.retrieve(retrieval_query)
        response = await self.llm_client.generate_chat_response(
            message=payload.message,
            context=payload.context,
            verses=verses,
        )
        self.logger.info("chat.generated_response verses=%s retrieval_query_changed=%s", len(verses), retrieval_query != payload.message)
        return ChatResponse(response=response, verses=verses, retrieval_query=retrieval_query)

    async def stream_response(self, payload: ChatRequest):
        retrieval_query = await self.query_rewrite_service.rewrite(payload.message)
        verses = await self.retriever.retrieve(retrieval_query)
        self.logger.info("chat.stream_started verses=%s retrieval_query_changed=%s", len(verses), retrieval_query != payload.message)
        return retrieval_query, verses, self.llm_client.stream_chat_response(
            message=payload.message,
            context=payload.context,
            verses=verses,
        )

    async def retrieve_relevant_verses(self, query: str) -> RetrieveResponse:
        retrieval_query = await self.query_rewrite_service.rewrite(query)
        results = await self.retriever.retrieve(retrieval_query)
        return RetrieveResponse(results=results, retrieval_query=retrieval_query)

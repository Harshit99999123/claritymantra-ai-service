from core.logging import get_logger
from models.chat import ChatRequest, ChatResponse
from models.retrieve import RetrieveResponse


class ChatService:
    def __init__(self, retriever, llm_client) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.logger = get_logger(__name__)

    async def generate_response(self, payload: ChatRequest) -> ChatResponse:
        verses = await self.retriever.retrieve(payload.message)
        response = await self.llm_client.generate_chat_response(
            message=payload.message,
            context=payload.context,
            verses=verses,
        )
        self.logger.info("chat.generated_response verses=%s", len(verses))
        return ChatResponse(response=response, verses=verses)

    async def retrieve_relevant_verses(self, query: str) -> RetrieveResponse:
        results = await self.retriever.retrieve(query)
        return RetrieveResponse(results=results)

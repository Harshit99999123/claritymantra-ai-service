from models.insight import InsightRequest, InsightResponse


class InsightService:
    def __init__(self, retriever, llm_client, query_rewrite_service) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.query_rewrite_service = query_rewrite_service

    async def generate_insight(self, payload: InsightRequest) -> InsightResponse:
        theme = payload.conversation[-1].message if payload.conversation else "daily reflection"
        retrieval_query = await self.query_rewrite_service.rewrite(theme)
        verses = await self.retriever.retrieve(retrieval_query)
        insight = await self.llm_client.generate_insight(payload.conversation, verses)
        return InsightResponse(**insight)

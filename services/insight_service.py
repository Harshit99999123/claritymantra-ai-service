from models.insight import InsightRequest, InsightResponse


class InsightService:
    def __init__(self, retriever, llm_client) -> None:
        self.retriever = retriever
        self.llm_client = llm_client

    async def generate_insight(self, payload: InsightRequest) -> InsightResponse:
        theme = payload.conversation[-1].message if payload.conversation else "daily reflection"
        verses = await self.retriever.retrieve(theme)
        insight = await self.llm_client.generate_insight(payload.conversation, verses)
        return InsightResponse(**insight)

from core.logging import get_logger


class GitaRetriever:
    def __init__(self, vector_store, embeddings) -> None:
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.logger = get_logger(__name__)

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, str]]:
        embedding = await self.embeddings.embed(query)
        results = await self.vector_store.search(embedding, top_k=top_k)
        self.logger.info("rag.retrieved query_length=%s results=%s", len(query), len(results))
        return results

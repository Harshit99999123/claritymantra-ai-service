from core.logging import get_logger
from models.knowledge import RetrievedKnowledgeChunk


class KnowledgeRetriever:
    def __init__(self, vector_store, embeddings, top_k: int, context_token_limit: int, candidate_pool: int) -> None:
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.top_k = top_k
        self.context_token_limit = context_token_limit
        self.candidate_pool = candidate_pool
        self.logger = get_logger(__name__)

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedKnowledgeChunk]:
        embedding = await self.embeddings.embed(query)
        results = await self.vector_store.search(
            query=query,
            embedding=embedding,
            top_k=top_k or self.top_k,
            candidate_pool=self.candidate_pool,
        )
        trimmed = enforce_token_budget(results, self.context_token_limit)
        self.logger.info("rag.retrieved query_length=%s results=%s", len(query), len(trimmed))
        return trimmed


def enforce_token_budget(results: list[RetrievedKnowledgeChunk], token_limit: int) -> list[RetrievedKnowledgeChunk]:
    selected: list[RetrievedKnowledgeChunk] = []
    token_count = 0
    for verse in results:
        estimated_tokens = estimate_tokens(verse.translation) + estimate_tokens(verse.interpretation)
        if selected and token_count + estimated_tokens > token_limit:
            break
        selected.append(verse)
        token_count += estimated_tokens
    return selected


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))

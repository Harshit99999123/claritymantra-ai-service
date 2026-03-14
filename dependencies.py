import asyncio
from dataclasses import dataclass

from core.config import Settings
from core.logging import get_logger
from ingestion.registry import get_book_definition
from llm.ollama_client import OllamaClient
from rag.dataset import load_dataset
from rag.embeddings import EmbeddingService
from rag.retriever import KnowledgeRetriever
from rag.vector_store import ChromaVectorStore
from services.chat_service import ChatService
from services.health_service import HealthService
from services.ingestion_service import IngestionService
from services.insight_service import InsightService
from services.query_rewrite_service import QueryRewriteService
from services.speech_service import SpeechService


@dataclass
class ServiceContainer:
    settings: Settings
    health_service: HealthService
    chat_service: ChatService
    ingestion_service: IngestionService
    insight_service: InsightService
    speech_service: SpeechService


def build_container(settings: Settings) -> ServiceContainer:
    logger = get_logger(__name__)
    vector_store = ChromaVectorStore(persist_path=settings.vector_store_path)
    embeddings = EmbeddingService(provider=settings.embedding_provider, model_name=settings.embedding_model)
    active_book = get_book_definition(settings.active_book_slug)
    chunks = load_dataset(
        dataset_path=active_book.output_dataset_path,
        source_slug=active_book.slug,
        source_title=active_book.title,
        source_kind=active_book.source_kind,
    )
    manifest = vector_store.read_manifest() or {}
    requires_reindex = (
        not vector_store.has_index()
        or manifest.get("embedding_provider") != settings.embedding_provider
        or manifest.get("embedding_model") != settings.embedding_model
        or manifest.get("record_count") != len(chunks)
        or manifest.get("active_book_slug") != settings.active_book_slug
    )
    if requires_reindex:
        asyncio.run(vector_store.index(chunks, embeddings))
        vector_store.write_manifest(
            {
                "collection_name": vector_store.collection_name,
                "embedding_provider": settings.embedding_provider,
                "embedding_model": settings.embedding_model,
                "record_count": len(chunks),
                "active_book_slug": settings.active_book_slug,
            }
        )
        logger.info(
            "dependencies.bootstrap_index indexed_records=%s provider=%s model=%s",
            len(chunks),
            settings.embedding_provider,
            settings.embedding_model,
        )
    else:
        logger.info("dependencies.bootstrap_index reused_existing_index=true")
    retriever = KnowledgeRetriever(
        vector_store=vector_store,
        embeddings=embeddings,
        top_k=settings.retrieval_top_k,
        context_token_limit=settings.retrieval_context_token_limit,
        candidate_pool=settings.retrieval_candidate_pool,
    )
    llm_client = OllamaClient(
        base_url=str(settings.ollama_base_url),
        model_name=settings.ollama_model,
        query_rewrite_model=settings.query_rewrite_model,
        keep_alive=settings.ollama_keep_alive,
        chat_temperature=settings.chat_temperature,
        chat_max_tokens=settings.chat_max_tokens,
        query_rewrite_max_tokens=settings.query_rewrite_max_tokens,
    )
    query_rewrite_service = QueryRewriteService(
        llm_client=llm_client,
        enabled=settings.enable_query_rewrite,
    )

    return ServiceContainer(
        settings=settings,
        health_service=HealthService(service_name=settings.service_name),
        chat_service=ChatService(
            retriever=retriever,
            llm_client=llm_client,
            query_rewrite_service=query_rewrite_service,
        ),
        ingestion_service=IngestionService(settings=settings, vector_store=vector_store, embeddings=embeddings),
        insight_service=InsightService(
            retriever=retriever,
            llm_client=llm_client,
            query_rewrite_service=query_rewrite_service,
        ),
        speech_service=SpeechService(),
    )

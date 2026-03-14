from dataclasses import dataclass

from core.config import Settings
from llm.ollama_client import OllamaClient
from rag.embeddings import EmbeddingService
from rag.retriever import GitaRetriever
from rag.vector_store import InMemoryVectorStore
from services.chat_service import ChatService
from services.health_service import HealthService
from services.insight_service import InsightService
from services.speech_service import SpeechService


@dataclass
class ServiceContainer:
    settings: Settings
    health_service: HealthService
    chat_service: ChatService
    insight_service: InsightService
    speech_service: SpeechService


def build_container(settings: Settings) -> ServiceContainer:
    vector_store = InMemoryVectorStore()
    embeddings = EmbeddingService(model_name=settings.embedding_model)
    retriever = GitaRetriever(vector_store=vector_store, embeddings=embeddings)
    llm_client = OllamaClient(
        base_url=str(settings.ollama_base_url),
        model_name=settings.ollama_model,
    )

    return ServiceContainer(
        settings=settings,
        health_service=HealthService(service_name=settings.service_name),
        chat_service=ChatService(retriever=retriever, llm_client=llm_client),
        insight_service=InsightService(retriever=retriever, llm_client=llm_client),
        speech_service=SpeechService(),
    )

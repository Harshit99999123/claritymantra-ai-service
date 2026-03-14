from fastapi import APIRouter

from api.routes import chat, health, insight, retrieve, speech

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(insight.router, tags=["insight"])
api_router.include_router(speech.router, tags=["speech"])
api_router.include_router(retrieve.router, tags=["retrieve"])

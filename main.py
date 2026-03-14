from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.router import api_router
from core.config import get_settings
from core.logging import configure_logging, get_logger
from core.middleware import RequestContextMiddleware
from dependencies import build_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info("ai_service.startup", extra={"environment": settings.environment})
    yield
    logger.info("ai_service.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="FastAPI service for philosophical reflection, RAG, and speech APIs.",
        lifespan=lifespan,
    )
    app.state.container = build_container(settings)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()

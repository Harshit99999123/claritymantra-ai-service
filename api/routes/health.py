from fastapi import APIRouter, Request

from models.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    return request.app.state.container.health_service.status()

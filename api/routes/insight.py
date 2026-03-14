from fastapi import APIRouter, Request

from models.insight import InsightRequest, InsightResponse

router = APIRouter(prefix="/ai")


@router.post("/insight", response_model=InsightResponse)
async def generate_insight(request: Request, payload: InsightRequest) -> InsightResponse:
    service = request.app.state.container.insight_service
    return await service.generate_insight(payload)

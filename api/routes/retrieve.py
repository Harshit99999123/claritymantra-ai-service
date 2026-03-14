from fastapi import APIRouter, Request

from models.retrieve import RetrieveRequest, RetrieveResponse

router = APIRouter(prefix="/ai")


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: Request, payload: RetrieveRequest) -> RetrieveResponse:
    service = request.app.state.container.chat_service
    return await service.retrieve_relevant_verses(payload.query)

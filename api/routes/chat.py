from fastapi import APIRouter, Request

from models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/ai")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    service = request.app.state.container.chat_service
    return await service.generate_response(payload)

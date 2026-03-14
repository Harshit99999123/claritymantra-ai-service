import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/ai")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    service = request.app.state.container.chat_service
    return await service.generate_response(payload)


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> StreamingResponse:
    service = request.app.state.container.chat_service
    retrieval_query, verses, stream = await service.stream_response(payload)

    async def event_stream():
        meta = {
            "retrieval_query": retrieval_query,
            "references": [
                {
                    "source": item.source.title,
                    "reference": item.reference,
                }
                for item in verses
            ],
        }
        yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"
        async for chunk in stream:
            yield f"event: token\ndata: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

from fastapi import APIRouter, Request

from ingestion.models import IngestionBookResponse, IngestionRunRequest, IngestionRunResponse

router = APIRouter(prefix="/ingestion")


@router.get("/books", response_model=list[IngestionBookResponse])
async def list_ingestion_books(request: Request) -> list[IngestionBookResponse]:
    return request.app.state.container.ingestion_service.list_books()


@router.post("/run", response_model=IngestionRunResponse)
async def run_ingestion(request: Request, payload: IngestionRunRequest) -> IngestionRunResponse:
    service = request.app.state.container.ingestion_service
    return await service.run_ingestion(
        book_slug=payload.book_slug,
        refresh_active_index=payload.refresh_active_index,
    )

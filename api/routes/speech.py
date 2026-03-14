from fastapi import APIRouter, File, Request, UploadFile

from models.speech import SpeechTranscriptionResponse

router = APIRouter(prefix="/speech")


@router.post("/transcribe", response_model=SpeechTranscriptionResponse)
async def transcribe(request: Request, audio_file: UploadFile = File(...)) -> SpeechTranscriptionResponse:
    service = request.app.state.container.speech_service
    return await service.transcribe(audio_file)

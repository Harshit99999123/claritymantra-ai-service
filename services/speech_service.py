from fastapi import UploadFile

from models.speech import SpeechTranscriptionResponse


class SpeechService:
    async def transcribe(self, audio_file: UploadFile) -> SpeechTranscriptionResponse:
        await audio_file.read()
        return SpeechTranscriptionResponse(
            text="Speech transcription is not wired yet. This endpoint is scaffolded for Whisper integration."
        )

from fastapi import APIRouter, HTTPException
from schemas.whisper import WhisperRequest, WhisperResponse
from services.whisper_service import transcribe_audio

router = APIRouter(prefix="/transcribe", tags=["whisper"])

@router.post("/", response_model=WhisperResponse)
async def transcribe_audio_endpoint(payload: WhisperRequest):
    result = transcribe_audio(payload)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
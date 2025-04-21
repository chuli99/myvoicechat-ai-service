from fastapi import APIRouter, HTTPException
from schemas.tts import TTSRequest, TTSResponse
from services.tts_service import generate_tts

router = APIRouter(prefix="/tts", tags=["tts"])

@router.post("/", response_model=TTSResponse)
async def generate_tts_endpoint(payload: TTSRequest):
    result = generate_tts(payload)
    if result["returncode"]!= 0:
        # Sólo hay error real si el CLI devuelve código distinto de cero
        raise HTTPException(status_code=500, detail=result["stderr"])
    return result
from fastapi import APIRouter, HTTPException
from schemas.audio_translation import TranslateAudioRequest, TranslateAudioResponse
from services.audio_translation_service import process_audio_translation

router = APIRouter(prefix="/translate-audio", tags=["audio-translation"])

@router.post("/", response_model=TranslateAudioResponse)
async def translate_audio_endpoint(payload: TranslateAudioRequest):
    """
    Endpoint que realiza el proceso completo:
    1. Transcribe el audio de entrada (Whisper)
    2. Traduce el texto transcrito (M2M100)
    3. Genera un audio con la traducción (F5TTS)
    
    El resultado incluye todos los textos generados y tiempos de procesamiento.
    """
    try:
        result = process_audio_translation(payload)
        
        # Verificar si hubo un error en el procesamiento
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        # Capturar cualquier excepción no controlada
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el proceso de traducción de audio: {str(e)}"
        )
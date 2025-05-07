from fastapi import APIRouter, HTTPException
from schemas.unified import UnifiedTranslationRequest, UnifiedTranslationResponse
from services.unified_service import process_unified_translation

router = APIRouter(prefix="/unified", tags=["unified"])

@router.post("/translate-audio", response_model=UnifiedTranslationResponse)
async def unified_translation_endpoint(payload: UnifiedTranslationRequest):
    """
    Endpoint unificado que realiza el proceso completo:
    1. Transcribe el audio de entrada (Whisper)
    2. Traduce el texto transcrito (M2M100)
    3. Genera un audio con la traducción (F5TTS)
    
    El resultado incluye todos los textos generados y tiempos de procesamiento.
    """
    try:
        result = process_unified_translation(payload)
        
        # Verificar si hubo un error en el procesamiento
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        # Capturar cualquier excepción no controlada
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el proceso unificado: {str(e)}"
        )
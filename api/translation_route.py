from fastapi import APIRouter, HTTPException
from schemas.translation import TranslationRequest, TranslationResponse
from services.translation_service import translate_text

router = APIRouter(prefix="/translate", tags=["translation"])

@router.post("/", response_model=TranslationResponse)
async def translate_text_endpoint(payload: TranslationRequest):
    try:
        result = translate_text(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la traducción: {str(e)}")
from pydantic import BaseModel, Field

class TranslationRequest(BaseModel):
    text: str = Field(..., example="Hello, this is a text to translate.", description="Texto a traducir")
    source_lang: str = Field(..., example="en", description="Código del idioma de origen (en, es, zh, etc.)")
    target_lang: str = Field(..., example="es", description="Código del idioma de destino (en, es, zh, etc.)")

class TranslationResponse(BaseModel):
    original_text: str = Field(..., description="Texto original enviado para traducción")
    translated_text: str = Field(..., description="Texto traducido")
    source_lang: str = Field(..., description="Idioma de origen")
    target_lang: str = Field(..., description="Idioma de destino")
    response_time: float = Field(..., description="Tiempo de respuesta en segundos")
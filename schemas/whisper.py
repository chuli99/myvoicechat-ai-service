from pydantic import BaseModel, Field

class WhisperRequest(BaseModel):
    audio_path: str = Field(..., example="audios/audioJulian.ogg", description="Ruta al archivo de audio a transcribir")

class WhisperResponse(BaseModel):
    text: str = Field(..., description="Texto transcrito del audio")
    response_time: float = Field(..., description="Tiempo de respuesta")
from pydantic import BaseModel, Field

class TTSRequest(BaseModel):
    model: str = Field(..., example="F5TTS_v1_Base")
    ref_audio_path: str = Field(..., example="audios/audioStefano.mp3")
    ref_text: str = Field(..., example="Texto de referencia")
    gen_text: str = Field(..., example="Texto a sintetizar")

class TTSResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int
    output_files: list[str]
    response_time: float = Field(..., description="Tiempo de respuesta en segundos")

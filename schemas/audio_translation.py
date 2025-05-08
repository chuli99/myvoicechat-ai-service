from pydantic import BaseModel, Field

class TranslateAudioRequest(BaseModel):
    """
    Solicitud para el proceso unificado de transcripción, traducción y síntesis de voz.
    """
    audio_path: str = Field(..., example="audios/audioStefano.mp3", 
                           description="Ruta al archivo de audio a transcribir")
    source_lang: str = Field(..., example="es", 
                            description="Código del idioma de origen (en, es, zh, etc.)")
    target_lang: str = Field(..., example="en", 
                            description="Código del idioma de destino (en, es, zh, etc.)")
    voice_reference_path: str = Field(..., example="audios/audioStefano.mp3", 
                                    description="Ruta al audio de referencia para la síntesis de voz")
    model: str = Field("F5TTS_v1_Base", example="F5TTS_v1_Base", 
                      description="Modelo TTS a utilizar")

class TranslateAudioResponse(BaseModel):
    """
    Respuesta del proceso de traducción de audio con todos los detalles del proceso.
    """
    # Información del audio original
    original_audio_path: str = Field(..., description="Ruta del archivo de audio original")
    
    # Resultados de la transcripción
    transcribed_text: str = Field(..., description="Texto transcrito del audio original")
    transcription_time: float = Field(..., description="Tiempo de transcripción en segundos")
    
    # Resultados de la traducción
    translated_text: str = Field(..., description="Texto traducido")
    source_lang: str = Field(..., description="Idioma de origen")
    target_lang: str = Field(..., description="Idioma de destino")
    translation_time: float = Field(..., description="Tiempo de traducción en segundos")
    
    # Resultados de la síntesis de voz
    output_audio_path: str = Field(..., description="Ruta del archivo de audio generado con la traducción")
    tts_time: float = Field(..., description="Tiempo de síntesis de voz en segundos")
    
    # Información general
    total_time: float = Field(..., description="Tiempo total del proceso en segundos")
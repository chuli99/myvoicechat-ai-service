from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path
from schemas.audio_translation import TranslateAudioResponse
from services.audio_translation_service import process_audio_translation_with_files

router = APIRouter(prefix="/translate-audio", tags=["audio-translation"])

@router.post("/")
async def translate_audio_endpoint(
    audio_file: UploadFile = File(..., description="Archivo de audio a transcribir y traducir"),
    source_lang: str = Form(..., description="Código del idioma de origen (ej: 'es', 'en', 'zh')"),
    target_lang: str = Form(..., description="Código del idioma de destino (ej: 'es', 'en', 'zh')"),
    voice_reference_file: UploadFile = File(..., description="Archivo de audio de referencia para la síntesis de voz"),
    model: str = Form("F5TTS_v1_Base", description="Modelo TTS a utilizar")
):
    """
    Endpoint que realiza el proceso completo:
    1. Transcribe el audio de entrada (Whisper)
    2. Traduce el texto transcrito (M2M100)
    3. Genera un audio con la traducción (F5TTS)
    
    Retorna directamente el archivo de audio generado con la traducción.
    """
    try:
        # Validar tipos de archivo
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="El archivo debe ser de tipo audio"
            )
        
        if not voice_reference_file.content_type or not voice_reference_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="El archivo de referencia de voz debe ser de tipo audio"
            )
        
        result = await process_audio_translation_with_files(
            audio_file=audio_file,
            voice_reference_file=voice_reference_file,
            source_lang=source_lang,
            target_lang=target_lang,
            model=model
        )
        
        # Verificar si hubo un error en el procesamiento
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Obtener la ruta del archivo de audio generado
        output_audio_path = result.get("output_audio_path")
        if not output_audio_path or not Path(output_audio_path).exists():
            raise HTTPException(
                status_code=500, 
                detail="Error: No se pudo generar el archivo de audio"
            )
        
        # Crear nombre de archivo descriptivo
        original_filename = audio_file.filename or "audio"
        base_name = Path(original_filename).stem
        output_filename = f"{base_name}_translated_{source_lang}_to_{target_lang}.wav"
        
        # Función auxiliar para limpiar texto para headers HTTP
        def clean_text_for_header(text: str, max_length: int = 200) -> str:
            """Limpia el texto para que sea válido en headers HTTP"""
            if not text:
                return ""
            # Remover caracteres no ASCII, limitar longitud y escapar caracteres problemáticos
            clean_text = text.encode('ascii', 'ignore').decode('ascii')
            # Remover caracteres de control y espacios extra
            clean_text = ' '.join(clean_text.split())
            # Escapar comillas y caracteres problemáticos
            clean_text = clean_text.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
            return clean_text[:max_length]
        
        # Retornar el archivo directamente
        return FileResponse(
            path=output_audio_path,
            media_type="audio/wav",
            filename=output_filename,
            headers={
                "X-Transcribed-Text": clean_text_for_header(result.get("transcribed_text", "")),
                "X-Translated-Text": clean_text_for_header(result.get("translated_text", "")),
                "X-Source-Lang": source_lang,
                "X-Target-Lang": target_lang,
                "X-Total-Time": str(result.get("total_time", 0))
            }
        )
            
    except Exception as e:
        # Capturar cualquier excepción no controlada
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el proceso de traducción de audio: {str(e)}"
        )


@router.post("/info", response_model=TranslateAudioResponse)
async def translate_audio_info_endpoint(
    audio_file: UploadFile = File(..., description="Archivo de audio a transcribir y traducir"),
    source_lang: str = Form(..., description="Código del idioma de origen (ej: 'es', 'en', 'zh')"),
    target_lang: str = Form(..., description="Código del idioma de destino (ej: 'es', 'en', 'zh')"),
    voice_reference_file: UploadFile = File(..., description="Archivo de audio de referencia para la síntesis de voz"),
    model: str = Form("F5TTS_v1_Base", description="Modelo TTS a utilizar")
):
    """
    Endpoint que realiza el proceso completo y retorna información JSON (para ver en Swagger UI):
    1. Transcribe el audio de entrada (Whisper)
    2. Traduce el texto transcrito (M2M100)
    3. Genera un audio con la traducción (F5TTS)
    
    Retorna información detallada del proceso en formato JSON.
    Para descargar el archivo de audio directamente, usa el endpoint POST / (sin /info).
    """
    try:
        # Validar tipos de archivo
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="El archivo debe ser de tipo audio"
            )
        
        if not voice_reference_file.content_type or not voice_reference_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="El archivo de referencia de voz debe ser de tipo audio"
            )
        
        result = await process_audio_translation_with_files(
            audio_file=audio_file,
            voice_reference_file=voice_reference_file,
            source_lang=source_lang,
            target_lang=target_lang,
            model=model
        )
        
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


@router.get("/download/{audio_id}")
async def download_translated_audio(audio_id: str):
    """
    Endpoint para descargar un audio generado previamente usando su ID.
    El ID se obtiene del campo output_audio_path del endpoint /info.
    """
    try:
        # Buscar el archivo en el directorio de salidas
        audio_path = None
        output_base_dir = Path("translate_audio_outputs")
        
        if output_base_dir.exists():
            # Buscar el archivo en todos los subdirectorios
            for subdir in output_base_dir.iterdir():
                if subdir.is_dir():
                    potential_file = subdir / "translated_audio.wav"
                    if potential_file.exists() and subdir.name == audio_id:
                        audio_path = potential_file
                        break
        
        if not audio_path or not audio_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Audio con ID {audio_id} no encontrado"
            )
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename=f"translated_audio_{audio_id}.wav"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al descargar el audio: {str(e)}"
        )
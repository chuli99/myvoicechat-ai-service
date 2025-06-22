import time
from pathlib import Path
import uuid
import os
import tempfile
import shutil
from typing import Dict, Any
from fastapi import UploadFile

from services.whisper_service import get_whisper_model
from services.translation_service import get_translation_model
from services.tts_service import get_tts

class WhisperRequest:
    """Clase auxiliar para adaptar la solicitud al formato que espera el servicio Whisper"""
    def __init__(self, audio_path: str):
        self.audio_path = audio_path

def process_audio_translation(request) -> Dict[str, Any]:
    """
    Procesa un flujo completo: transcripción (Whisper) → traducción (M2M100) → síntesis de voz (F5TTS)
    
    Args:
        request: La solicitud con todos los parámetros necesarios
        
    Returns:
        Un diccionario con todos los resultados del proceso
    """
    # Iniciar temporizador total
    total_start_time = time.time()
    result = {}
    
    # Verificar existencia de los archivos de audio
    audio_path = Path(request.audio_path)
    if not audio_path.exists():
        return {
            "error": f"El archivo de audio {request.audio_path} no existe"
        }
    
    voice_reference_path = Path(request.voice_reference_path)
    if not voice_reference_path.exists():
        return {
            "error": f"El archivo de referencia de voz {request.voice_reference_path} no existe"
        }
    
    # Preparar la respuesta con la ruta del audio original
    result["original_audio_path"] = str(audio_path)
    result["source_lang"] = request.source_lang
    result["target_lang"] = request.target_lang
    
    # 1. PASO UNO: TRANSCRIPCIÓN con Whisper
    print(f"🎙️ Transcribiendo audio: {audio_path}")
    transcription_start = time.time()
    
    # Crear objeto de solicitud para el servicio Whisper
    whisper_request = WhisperRequest(str(audio_path))
    
    # Obtener modelo cargado (usar la función que evita recargar)
    whisper_model = get_whisper_model()
    
    # Realizar transcripción
    transcription_result = whisper_model.transcribe(str(audio_path), fp16=False)
    transcribed_text = transcription_result["text"]
    
    # Calcular tiempo de transcripción
    transcription_time = time.time() - transcription_start
    print(f"✅ Transcripción completada en {transcription_time:.2f}s: {transcribed_text[:50]}...")
    
    # Almacenar resultados de la transcripción
    result["transcribed_text"] = transcribed_text
    result["transcription_time"] = round(transcription_time, 2)
    
    # 2. PASO DOS: TRADUCCIÓN con M2M100
    print(f"🌐 Traduciendo de {request.source_lang} a {request.target_lang}")
    translation_start = time.time()
    
    # Obtener modelo, tokenizador y dispositivo
    model, tokenizer, device = get_translation_model()
    
    # Configurar idioma de origen
    tokenizer.src_lang = request.source_lang
    
    # Codificar texto transcrito
    encoded_text = tokenizer(transcribed_text, return_tensors="pt").to(device)
    
    # Generar traducción
    generated_tokens = model.generate(
        **encoded_text, 
        forced_bos_token_id=tokenizer.get_lang_id(request.target_lang)
    )
    
    # Decodificar traducción
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    
    # Calcular tiempo de traducción
    translation_time = time.time() - translation_start
    print(f"✅ Traducción completada en {translation_time:.2f}s: {translated_text[:50]}...")
    
    # Almacenar resultados de la traducción
    result["translated_text"] = translated_text
    result["translation_time"] = round(translation_time, 2)
    
    # 3. PASO TRES: SÍNTESIS DE VOZ con F5TTS
    print(f"🔊 Generando audio con la traducción")
    tts_start = time.time()
    
    # Primero, transcribir el audio de referencia para obtener un texto de referencia adecuado
    print(f"📝 Transcribiendo audio de referencia para obtener texto de referencia...")
    reference_transcription = whisper_model.transcribe(str(voice_reference_path), fp16=False)
    reference_text = reference_transcription["text"]
    print(f"✅ Texto de referencia obtenido: {reference_text[:50]}...")
    
    # Obtener instancia TTS con el modelo apropiado para el idioma de destino
    print(f"🎯 Cargando modelo TTS para idioma de destino: {request.target_lang}")
    tts = get_tts(request.target_lang)
    
    # Mensaje informativo sobre el modelo cargado
    model_name = "F5TTS_Spanish" if request.target_lang == "es" else "F5TTS_Base"
    print(f"✅ Modelo TTS cargado: {model_name} para idioma {request.target_lang}")
    
    # Crear directorio único para la salida
    output_dir = Path("translate_audio_outputs") / uuid.uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "translated_audio.wav"
    
    # Generar síntesis de voz:
    # - Usa el texto transcrito del audio de referencia como ref_text
    # - Usa el texto traducido como texto a generar (gen_text)
    try:
        tts.infer(
            ref_file=str(voice_reference_path),
            ref_text=reference_text,  # Texto transcrito del audio de referencia
            gen_text=translated_text,  # Texto traducido para generar
            file_wave=str(output_file)
        )
    except Exception as e:
        return {
            "error": f"Error al generar audio: {str(e)}",
            "transcribed_text": transcribed_text,
            "translated_text": translated_text,
            "transcription_time": round(transcription_time, 2),
            "translation_time": round(translation_time, 2)
        }
    
    # Calcular tiempo de síntesis
    tts_time = time.time() - tts_start
    print(f"✅ Síntesis de voz completada en {tts_time:.2f}s: {output_file}")
    
    # Almacenar resultados de la síntesis
    result["output_audio_path"] = str(output_file)
    result["tts_time"] = round(tts_time, 2)
    result["reference_text"] = reference_text  # Añadir el texto de referencia a la respuesta
    
    # Calcular tiempo total
    total_time = time.time() - total_start_time
    result["total_time"] = round(total_time, 2)
    
    print(f"✅ Proceso de traducción de audio completado en {total_time:.2f}s")
    
    return result

async def process_audio_translation_file(request) -> Dict[str, Any]:
    """
    Procesa un flujo completo: transcripción (Whisper) → traducción (M2M100) → síntesis de voz (F5TTS)
    Recibiendo el archivo de audio como UploadFile
    
    Args:
        request: La solicitud con todos los parámetros necesarios
        
    Returns:
        Un diccionario con todos los resultados del proceso
    """
    # Iniciar temporizador total
    total_start_time = time.time()
    result = {}
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Archivos temporales en: {tmpdirname}")
        
        # Guardar archivo de audio subido
        audio_path = Path(tmpdirname) / "audio.wav"
        with audio_path.open("wb") as f:
            shutil.copyfileobj(request.audio_file, f)
        
        # Guardar archivo de referencia de voz subido
        voice_reference_path = Path(tmpdirname) / "reference.wav"
        with voice_reference_path.open("wb") as f:
            shutil.copyfileobj(request.voice_reference_file, f)
        
        # Verificar existencia de los archivos de audio
        if not audio_path.exists():
            return {
                "error": f"El archivo de audio no existe"
            }
        
        if not voice_reference_path.exists():
            return {
                "error": f"El archivo de referencia de voz no existe"
            }
        
        # Preparar la respuesta con la ruta del audio original
        result["original_audio_path"] = str(audio_path)
        result["source_lang"] = request.source_lang
        result["target_lang"] = request.target_lang
        
        # 1. PASO UNO: TRANSCRIPCIÓN con Whisper
        print(f"🎙️ Transcribiendo audio: {audio_path}")
        transcription_start = time.time()
        
        # Crear objeto de solicitud para el servicio Whisper
        whisper_request = WhisperRequest(str(audio_path))
        
        # Obtener modelo cargado (usar la función que evita recargar)
        whisper_model = get_whisper_model()
        
        # Realizar transcripción
        transcription_result = whisper_model.transcribe(str(audio_path), fp16=False)
        transcribed_text = transcription_result["text"]
        
        # Calcular tiempo de transcripción
        transcription_time = time.time() - transcription_start
        print(f"✅ Transcripción completada en {transcription_time:.2f}s: {transcribed_text[:50]}...")
        
        # Almacenar resultados de la transcripción
        result["transcribed_text"] = transcribed_text
        result["transcription_time"] = round(transcription_time, 2)
        
        # 2. PASO DOS: TRADUCCIÓN con M2M100
        print(f"🌐 Traduciendo de {request.source_lang} a {request.target_lang}")
        translation_start = time.time()
        
        # Obtener modelo, tokenizador y dispositivo
        model, tokenizer, device = get_translation_model()
        
        # Configurar idioma de origen
        tokenizer.src_lang = request.source_lang
        
        # Codificar texto transcrito
        encoded_text = tokenizer(transcribed_text, return_tensors="pt").to(device)
        
        # Generar traducción
        generated_tokens = model.generate(
            **encoded_text, 
            forced_bos_token_id=tokenizer.get_lang_id(request.target_lang)
        )
        
        # Decodificar traducción
        translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # Calcular tiempo de traducción
        translation_time = time.time() - translation_start
        print(f"✅ Traducción completada en {translation_time:.2f}s: {translated_text[:50]}...")
        
        # Almacenar resultados de la traducción
        result["translated_text"] = translated_text
        result["translation_time"] = round(translation_time, 2)
        
        # 3. PASO TRES: SÍNTESIS DE VOZ con F5TTS
        print(f"🔊 Generando audio con la traducción")
        tts_start = time.time()
        
        # Primero, transcribir el audio de referencia para obtener un texto de referencia adecuado
        print(f"📝 Transcribiendo audio de referencia para obtener texto de referencia...")
        reference_transcription = whisper_model.transcribe(str(voice_reference_path), fp16=False)
        reference_text = reference_transcription["text"]
        print(f"✅ Texto de referencia obtenido: {reference_text[:50]}...")
        
        # Obtener instancia TTS con el modelo apropiado para el idioma de destino
        print(f"🎯 Cargando modelo TTS para idioma de destino: {request.target_lang}")
        tts = get_tts(request.target_lang)
        
        # Mensaje informativo sobre el modelo cargado
        model_name = "F5TTS_Spanish" if request.target_lang == "es" else "F5TTS_Base"
        print(f"✅ Modelo TTS cargado: {model_name} para idioma {request.target_lang}")
        
        # Crear directorio único para la salida
        output_dir = Path("translate_audio_outputs") / uuid.uuid4().hex
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "translated_audio.wav"
        
        # Generar síntesis de voz:
        # - Usa el texto transcrito del audio de referencia como ref_text
        # - Usa el texto traducido como texto a generar (gen_text)
        try:
            tts.infer(
                ref_file=str(voice_reference_path),
                ref_text=reference_text,  # Texto transcrito del audio de referencia
                gen_text=translated_text,  # Texto traducido para generar
                file_wave=str(output_file)
            )
        except Exception as e:
            return {
                "error": f"Error al generar audio: {str(e)}",
                "transcribed_text": transcribed_text,
                "translated_text": translated_text,
                "transcription_time": round(transcription_time, 2),
                "translation_time": round(translation_time, 2)
            }
        
        # Calcular tiempo de síntesis
        tts_time = time.time() - tts_start
        print(f"✅ Síntesis de voz completada en {tts_time:.2f}s: {output_file}")
        
        # Almacenar resultados de la síntesis
        result["output_audio_path"] = str(output_file)
        result["tts_time"] = round(tts_time, 2)
        result["reference_text"] = reference_text  # Añadir el texto de referencia a la respuesta
        
        # Calcular tiempo total
        total_time = time.time() - total_start_time
        result["total_time"] = round(total_time, 2)
        
        print(f"✅ Proceso de traducción de audio completado en {total_time:.2f}s")
        
        return result


async def process_audio_translation_with_files(
    audio_file: UploadFile,
    voice_reference_file: UploadFile,
    source_lang: str,
    target_lang: str,
    model: str = "F5TTS_v1_Base"
) -> Dict[str, Any]:
    """
    Procesa un flujo completo: transcripción (Whisper) → traducción (M2M100) → síntesis de voz (F5TTS)
    usando archivos directamente recibidos como UploadFile
    
    Args:
        audio_file: Archivo de audio a transcribir y traducir
        voice_reference_file: Archivo de audio de referencia para la síntesis de voz
        source_lang: Código del idioma de origen
        target_lang: Código del idioma de destino
        model: Modelo TTS a utilizar
        
    Returns:
        Un diccionario con todos los resultados del proceso
    """
    # Iniciar temporizador total
    total_start_time = time.time()
    result = {}
    
    # Crear archivos temporales para procesar los uploads
    temp_audio_path = None
    temp_voice_ref_path = None
    
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        
        # Guardar archivo de audio temporal
        audio_extension = Path(audio_file.filename).suffix if audio_file.filename else '.wav'
        temp_audio_path = Path(temp_dir) / f"audio{audio_extension}"
        
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Guardar archivo de referencia de voz temporal
        voice_extension = Path(voice_reference_file.filename).suffix if voice_reference_file.filename else '.wav'
        temp_voice_ref_path = Path(temp_dir) / f"voice_ref{voice_extension}"
        
        with open(temp_voice_ref_path, "wb") as buffer:
            shutil.copyfileobj(voice_reference_file.file, buffer)
        
        # Preparar la respuesta
        result["original_audio_filename"] = audio_file.filename or "uploaded_audio"
        result["source_lang"] = source_lang
        result["target_lang"] = target_lang
        
        # 1. PASO UNO: TRANSCRIPCIÓN con Whisper
        print(f"🎙️ Transcribiendo audio: {audio_file.filename}")
        transcription_start = time.time()
        
        # Obtener modelo cargado (usar la función que evita recargar)
        whisper_model = get_whisper_model()
        
        # Realizar transcripción
        transcription_result = whisper_model.transcribe(str(temp_audio_path), fp16=False)
        transcribed_text = transcription_result["text"]
        
        # Calcular tiempo de transcripción
        transcription_time = time.time() - transcription_start
        print(f"✅ Transcripción completada en {transcription_time:.2f}s: {transcribed_text[:50]}...")
        
        # Almacenar resultados de la transcripción
        result["transcribed_text"] = transcribed_text
        result["transcription_time"] = round(transcription_time, 2)
        
        # 2. PASO DOS: TRADUCCIÓN con M2M100
        print(f"🌐 Traduciendo de {source_lang} a {target_lang}")
        translation_start = time.time()
        
        # Obtener modelo, tokenizador y dispositivo
        model_instance, tokenizer, device = get_translation_model()
        
        # Configurar idioma de origen
        tokenizer.src_lang = source_lang
        
        # Codificar texto transcrito
        encoded_text = tokenizer(transcribed_text, return_tensors="pt").to(device)
        
        # Generar traducción
        generated_tokens = model_instance.generate(
            **encoded_text, 
            forced_bos_token_id=tokenizer.get_lang_id(target_lang)
        )
        
        # Decodificar traducción
        translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # Calcular tiempo de traducción
        translation_time = time.time() - translation_start
        print(f"✅ Traducción completada en {translation_time:.2f}s: {translated_text[:50]}...")
        
        # Almacenar resultados de la traducción
        result["translated_text"] = translated_text
        result["translation_time"] = round(translation_time, 2)
        
        # 3. PASO TRES: SÍNTESIS DE VOZ con F5TTS
        print(f"🔊 Generando audio con la traducción")
        tts_start = time.time()
        
        # Transcribir el audio de referencia para obtener un texto de referencia adecuado
        print(f"📝 Transcribiendo audio de referencia para obtener texto de referencia...")
        #reference_transcription = whisper_model.transcribe(str(temp_voice_ref_path), fp16=False)
        #reference_text = reference_transcription["text"]
        reference_text = ("Mientras mas corto es el audio el modelo es mejor. ")
        print(f"✅ Texto de referencia obtenido: {reference_text[:50]}...")
        
        # Obtener instancia TTS con el modelo apropiado para el idioma de destino
        print(f"🎯 Cargando modelo TTS para idioma de destino: {target_lang}")
        tts = get_tts(target_lang)
        
        # Mensaje informativo sobre el modelo cargado
        model_name = "F5TTS_Spanish" if target_lang == "es" else "F5TTS_Base"
        print(f"✅ Modelo TTS cargado: {model_name} para idioma {target_lang}")
        
        # Crear directorio único para la salida
        output_dir = Path("translate_audio_outputs") / uuid.uuid4().hex
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "translated_audio.wav"
        
        # Generar síntesis de voz
        try:
            tts.infer(
                ref_file=str(temp_voice_ref_path),
                ref_text=reference_text,  # Texto transcrito del audio de referencia
                gen_text=translated_text,  # Texto traducido para generar
                file_wave=str(output_file)
            )
        except Exception as e:
            return {
                "error": f"Error al generar audio: {str(e)}",
                "transcribed_text": transcribed_text,
                "translated_text": translated_text,
                "transcription_time": round(transcription_time, 2),
                "translation_time": round(translation_time, 2)
            }
        
        # Calcular tiempo de síntesis
        tts_time = time.time() - tts_start
        print(f"✅ Síntesis de voz completada en {tts_time:.2f}s: {output_file}")
        
        # Almacenar resultados de la síntesis
        result["output_audio_path"] = str(output_file)
        result["tts_time"] = round(tts_time, 2)
        result["reference_text"] = reference_text  # Añadir el texto de referencia a la respuesta
        
        # Calcular tiempo total
        total_time = time.time() - total_start_time
        result["total_time"] = round(total_time, 2)
        
        print(f"✅ Proceso de traducción de audio completado en {total_time:.2f}s")
        
        return result
        
    finally:
        # Limpiar archivos temporales
        try:
            if temp_audio_path and temp_audio_path.exists():
                temp_audio_path.unlink()
            if temp_voice_ref_path and temp_voice_ref_path.exists():
                temp_voice_ref_path.unlink()
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Error limpiando archivos temporales: {e}")
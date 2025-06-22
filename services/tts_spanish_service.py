"""
Servicio TTS específico para español usando F5TTS
Este servicio está optimizado para cargar únicamente el modelo español
"""

import uuid
import time
from pathlib import Path
import io
from contextlib import redirect_stdout, redirect_stderr

from f5_tts.api import F5TTS

# Instancia del modelo español (singleton)
_spanish_tts_instance = None

def get_spanish_tts():
    """
    Obtiene la instancia de F5TTS configurada específicamente para español
    """
    global _spanish_tts_instance
    
    if _spanish_tts_instance is None:
        print("🔄 Inicializando modelo F5TTS para español...")
        try:
            _spanish_tts_instance = F5TTS(language="es")
            print("✅ Modelo español cargado correctamente")
        except Exception as e:
            print(f"❌ Error cargando modelo español: {str(e)}")
            raise e
    
    return _spanish_tts_instance

def generate_spanish_tts(request) -> dict:
    """
    Genera TTS en español usando el modelo especializado
    
    Args:
        request: Solicitud con los parámetros de TTS
    """
    start_time = time.time()
    
    # Obtener la instancia del modelo español
    api = get_spanish_tts()
    
    # Directorio para los archivos de salida
    output_dir = Path("tts_outputs") / uuid.uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "spanish_tts.wav"
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    returncode = 0
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Llamar a la API 
            api.infer(
                ref_file=request.ref_audio_path,  
                ref_text=request.ref_text,         
                gen_text=request.gen_text,
                speed=0.8,        
                file_wave=str(output_file)        
            )
            
        print(f"🎤 TTS español generado:")
        print(f"   - Archivo de referencia: {request.ref_audio_path}")
        print(f"   - Texto de referencia: {request.ref_text}")
        print(f"   - Texto a generar: {request.gen_text}")
        print(f"   - Archivo de salida: {output_file}")
        
    except Exception as e:
        stderr_capture.write(f"Error en F5TTS API (español): {str(e)}\n")
        returncode = 1
    
    # Obtener la lista de archivos generados
    files = [str(p) for p in output_dir.glob("*")]
    
    # Tiempo de respuesta
    response_time = round(time.time() - start_time, 2)
    
    # Response
    result = {
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue(),
        "returncode": returncode,
        "output_files": files,
        "response_time": response_time,
        "model_used": "F5TTS_Spanish",
        "language": "es"
    }
    
    return result

def preload_spanish_model():
    """
    Precarga el modelo español
    """
    print("🔄 Precargando modelo español...")
    get_spanish_tts()
    print("✅ Modelo español precargado")

import uuid
import time
from pathlib import Path
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
import inspect

# Importamos la API de F5TTS
from f5_tts.api import F5TTS

# Importo la configuración global
from core.config import settings

# Creamos una instancia singleton de F5TTS para reutilizarla entre llamadas
_f5tts_instance = None

def get_f5tts_instance():
    """Obtiene o crea la instancia de F5TTS (singleton)"""
    global _f5tts_instance
    if _f5tts_instance is None:
        # Inicializamos F5TTS sin argumentos
        _f5tts_instance = F5TTS()
    return _f5tts_instance

def generate_tts(request) -> dict:
    """Genera audio TTS usando directamente la API de F5TTS"""
    start_time = time.time()
    
    # Obtener la instancia de F5TTS (cargada una sola vez)
    api = get_f5tts_instance()
    
    # Crear directorio para los archivos de salida
    output_dir = Path("tts_outputs") / uuid.uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "infer_cli_basic.wav"
    
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
                file_wave=str(output_file)        
            )
    except Exception as e:
        
        stderr_capture.write(f"Error en F5TTS API: {str(e)}\n")
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
        "from_cache": False
    }
    
    return result
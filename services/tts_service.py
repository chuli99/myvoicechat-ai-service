import uuid
import time
from pathlib import Path
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
import inspect

from f5_tts.api import F5TTS

from core.config import settings

_f5tts_instance = None

def get_f5tts_instance():
    global _f5tts_instance
    if _f5tts_instance is None:
        _f5tts_instance = F5TTS()
    return _f5tts_instance

def generate_tts(request) -> dict:
    start_time = time.time()
    
    api = get_f5tts_instance()
    
    #Directorio para los archivos de salida
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
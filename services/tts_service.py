import subprocess
import uuid
import time
from pathlib import Path

#importo la configuracion global
from core.config import settings

def generate_tts(request) -> dict:
    start_time = time.time()
    
    output_dir = Path("tts_outputs") / uuid.uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.f5_tts_cmd,
        "--model", request.model,
        "--ref_audio", request.ref_audio_path,
        "--ref_text", request.ref_text,
        "--gen_text", request.gen_text,
        "--output_dir", str(output_dir),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    files = [str(p) for p in output_dir.glob("*")]
    
    end_time = time.time()
    response_time = round(end_time - start_time, 2)  # Redondear a 2 decimales

    return{
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
        "output_files": files,
        "response_time": response_time
    }
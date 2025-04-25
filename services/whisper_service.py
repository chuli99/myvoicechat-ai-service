import time
import whisper
from pathlib import Path

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        device = "cuda"
        try:
            _whisper_model = whisper.load_model("turbo", device=device)
            print(f"Modelo Whisper cargado GPU con {device}")
        except Exception as e:
            # Si falla con cuda, intentar con CPU
            print(f"Error al cargar en GPU: {str(e)}")
            device = "cpu"
            print("Cargando en CPU")
            _whisper_model = whisper.load_model("turbo", device=device)
    return _whisper_model

def transcribe_audio(request) -> dict:
    start_time = time.time()
    
    # Verificar existencia del arhivo
    audio_path = Path(request.audio_path)
    if not audio_path.exists():
        return {
            "text": "",
            "error": f"El archivo {request.audio_path} no existe",
            "response_time": round(time.time() - start_time, 2)
        }
    
    # Cargar el modelo 
    model = get_whisper_model()
    
    # Transcripcion
    result = model.transcribe(str(audio_path), fp16=False)
    
    # Tiempo de respuesta
    response_time = round(time.time() - start_time, 2)
    
    return {
        "text": result["text"],
        "response_time": response_time
    }
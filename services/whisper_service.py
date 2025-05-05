import time
import whisper
from pathlib import Path

_whisper_model = None
_is_preloaded = False  # Nueva bandera para indicar si el modelo fue precargado

def load_whisper_model(force_load=False):
    global _whisper_model, _is_preloaded
    
    # Si el modelo ya está cargado y no se fuerza la recarga, solo lo devolvemos
    if _whisper_model is not None and not force_load:
        return _whisper_model
    
    device = "cuda"
    try:
        _whisper_model = whisper.load_model("turbo", device=device)
        print(f"Modelo Whisper cargado en GPU con {device}")
    except Exception as e:
        # Si falla con cuda, intentar con CPU
        print(f"Error al cargar en GPU: {str(e)}")
        device = "cpu"
        print("Cargando en CPU")
        _whisper_model = whisper.load_model("turbo", device=device)
    
    _is_preloaded = True
    return _whisper_model

# Mantenemos get_whisper_model para compatibilidad
def get_whisper_model():
    return load_whisper_model()

def transcribe_audio(request) -> dict:
    start_time = time.time()
    
    # Verificar existencia del archivo
    audio_path = Path(request.audio_path)
    if not audio_path.exists():
        return {
            "text": "",
            "error": f"El archivo {request.audio_path} no existe",
            "response_time": round(time.time() - start_time, 2)
        }
    
    # Cargar el modelo (no se recargará si ya está cargado)
    model = get_whisper_model()
    
    # Transcripcion
    result = model.transcribe(str(audio_path), fp16=False)
    
    # Tiempo de respuesta
    response_time = round(time.time() - start_time, 2)
    
    return {
        "text": result["text"],
        "response_time": response_time
    }
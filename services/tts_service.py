import uuid
import time
from pathlib import Path
import io
from contextlib import redirect_stdout, redirect_stderr

from f5_tts.api import F5TTS
from core.config import settings

# Diccionario para mantener múltiples instancias de modelos
_f5tts_instances = {}
_is_preloaded = False

# Configuración de modelos simplificada
MODEL_CONFIGS = {
    "spanish": {
        "name": "F5TTS_Spanish",
        "language_code": "es"
    },
    "base": {
        "name": "F5TTS_Base", 
        "language_code": "en"
    }
}

def get_model_name_for_language(target_lang: str) -> str:
    """
    Determina qué modelo usar basado en el idioma de destino
    """
    if target_lang == "es":
        return "spanish"
    else:  # en, zh, u otros
        return "base"

def get_tts(target_lang: str = "en", force_load=False):
    """
    Obtiene la instancia de F5TTS para el idioma especificado
    
    Args:
        target_lang: Idioma de destino ('es', 'en', 'zh', etc.)
        force_load: Forzar recarga del modelo
    """
    global _f5tts_instances, _is_preloaded
    
    model_type = get_model_name_for_language(target_lang)
    
    print(f"🔍 get_tts llamado con target_lang='{target_lang}', model_type='{model_type}', force_load={force_load}")
    print(f"📋 Instancias en caché: {list(_f5tts_instances.keys())}")
    
    # Si la instancia ya existe y no se fuerza recarga, devolverla
    if model_type in _f5tts_instances and not force_load:
        print(f"♻️ Usando modelo F5TTS en caché: {MODEL_CONFIGS[model_type]['name']} para idioma: {target_lang}")
        print(f"🔗 Instancia: {id(_f5tts_instances[model_type])}")
        return _f5tts_instances[model_type]
    
    print(f"🔄 Inicializando NUEVO modelo F5TTS: {MODEL_CONFIGS[model_type]['name']} para idioma: {target_lang}")
    
    try:
        # Crear nueva instancia con el parámetro de idioma
        new_instance = F5TTS(language=MODEL_CONFIGS[model_type]['language_code'])
        _f5tts_instances[model_type] = new_instance
        
        _is_preloaded = True
        print(f"✅ Modelo {MODEL_CONFIGS[model_type]['name']} cargado correctamente para idioma: {target_lang}")
        print(f"🔗 Nueva instancia: {id(new_instance)}")
        print(f"📋 Instancias después de carga: {list(_f5tts_instances.keys())}")
        return new_instance
        
    except Exception as e:
        print(f"❌ Error cargando modelo {MODEL_CONFIGS[model_type]['name']}: {str(e)}")
        raise e

# Función para precargar ambos modelos
def preload_all_models():
    """
    Precarga todos los modelos F5TTS disponibles
    """
    print("Precargando todos los modelos F5TTS...")
    
    try:
        # Cargar modelo para español
        get_tts("es")
        
        # Cargar modelo para inglés/chino
        get_tts("en")
        
        print("✅ Todos los modelos F5TTS cargados correctamente")
        
    except Exception as e:
        print(f"❌ Error precargando modelos: {str(e)}")
        raise e

# Mantenemos get_f5tts_instance para compatibilidad (usa inglés por defecto)
def get_f5tts_instance(target_lang: str = "en"):
    return get_tts(target_lang)

def generate_tts(request, target_lang: str = "en") -> dict:
    """
    Genera TTS usando el modelo apropiado para el idioma
    
    Args:
        request: Solicitud con los parámetros de TTS
        target_lang: Idioma de destino para seleccionar el modelo correcto
    """
    start_time = time.time()
    
    # Obtener la instancia correcta según el idioma
    api = get_tts(target_lang)
    
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
                speed=0.8,        
                file_wave=str(output_file)        
            )
            
        model_type = get_model_name_for_language(target_lang)
        print(f"TTS generado con modelo: {MODEL_CONFIGS[model_type]['name']}")
        print(f"Idioma destino: {target_lang}")
        print(f"Archivo de referencia: {request.ref_audio_path}")
        print(f"Texto de referencia: {request.ref_text}")
        print(f"Texto a generar: {request.gen_text}")
        
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
        "from_cache": False,
        "model_used": MODEL_CONFIGS[get_model_name_for_language(target_lang)]['name'],
        "target_language": target_lang
    }
    
    return result

def setup_initial_models():
    """
    Función auxiliar para verificar que los modelos estén disponibles.
    Ya no es necesario hacer backups, solo verificar que existan los archivos.
    """
    print("🔧 Verificando disponibilidad de modelos F5TTS...")
    
    try:
        # Intentar cargar ambos modelos para verificar que están disponibles
        print("Verificando modelo inglés...")
        get_tts("en")
        
        print("Verificando modelo español...")
        get_tts("es")
        
        print("✅ Configuración verificada! Ambos modelos están disponibles")
        return True
        
    except Exception as e:
        print(f"❌ Error en la configuración: {str(e)}")
        print("Asegúrate de que ambos modelos estén en las siguientes ubicaciones:")
        print("- Inglés: ~/.cache/huggingface/hub/models--SWivid--F5-TTS/snapshots/.../F5TTS_Base/model_1200000.safetensors")
        print("- Español: ~/.cache/huggingface/hub/models--SWivid--F5-TTS/snapshots/.../F5TTS_Spanish/model_spanish.safetensors")
        return False
import uuid
import time
from pathlib import Path
import io
import sys
import os
import shutil
from contextlib import redirect_stdout, redirect_stderr
import inspect
from cached_path import cached_path

from f5_tts.api import F5TTS
from core.config import settings

# Diccionario para mantener múltiples instancias de modelos
_f5tts_instances = {}
_is_preloaded = False

# Configuración de modelos
MODEL_CONFIGS = {
    "spanish": {
        "hf_path": "hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors",
        "cache_filename": "model_spanish.safetensors",  # Nombre específico para español
        "name": "F5TTS_Spanish"
    },
    "base": {
        "hf_path": "hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors", 
        "cache_filename": "model_1200000.safetensors",  # Nombre original
        "name": "F5TTS_Base"
    }
}

def get_cache_directory():
    """
    Obtiene el directorio de caché de HuggingFace donde están los modelos
    """
    # Primero obtener la ruta del modelo para saber dónde está el caché
    cache_path = cached_path(MODEL_CONFIGS["base"]["hf_path"])
    cache_dir = Path(cache_path).parent
    return cache_dir

def setup_model_files():
    """
    Configura los archivos de modelo necesarios en el directorio de caché
    """
    cache_dir = get_cache_directory()
    
    # Rutas de los archivos en el caché
    original_model = cache_dir / "model_1200000.safetensors"
    spanish_model = cache_dir / "model_spanish.safetensors" 
    base_backup = cache_dir / "model_base_backup.safetensors"
    
    print(f"Directorio de caché: {cache_dir}")
    print(f"Modelo original: {original_model}")
    print(f"Modelo español: {spanish_model}")
    
    return {
        "cache_dir": cache_dir,
        "original_model": original_model,
        "spanish_model": spanish_model,
        "base_backup": base_backup
    }

def backup_and_restore_model(model_type: str):
    """
    Configura el modelo correcto en el caché de HuggingFace
    """
    files_info = setup_model_files()
    cache_dir = files_info["cache_dir"]
    original_model = files_info["original_model"]
    spanish_model = files_info["spanish_model"]
    base_backup = files_info["base_backup"]
    
    if model_type == "spanish":
        # Verificar si el modelo español existe
        if not spanish_model.exists():
            print(f"❌ Modelo español no encontrado en {spanish_model}")
            print(f"Por favor, coloca tu modelo español (.safetensors) en: {spanish_model}")
            print("Puedes renombrar tu archivo de modelo español actual a 'model_spanish.safetensors'")
            return False
        
        # Hacer backup del modelo base si no existe
        if original_model.exists() and not base_backup.exists():
            print("Haciendo backup del modelo base original...")
            shutil.copy2(original_model, base_backup)
        
        # Copiar el modelo español como el modelo principal
        print(f"Configurando modelo español...")
        shutil.copy2(spanish_model, original_model)
        print(f"✅ Modelo español configurado")
        
    elif model_type == "base":
        # Restaurar el modelo base desde el backup
        if base_backup.exists():
            print(f"Restaurando modelo base original...")
            shutil.copy2(base_backup, original_model)
            print(f"✅ Modelo base restaurado")
        else:
            # Si no hay backup, verificar que el modelo original esté presente
            if not original_model.exists():
                print(f"❌ Modelo base no encontrado en {original_model}")
                print("El modelo base original no está disponible")
                return False
            print(f"✅ Modelo base ya está configurado")
    
    return True

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
    
    # Si la instancia ya existe y no se fuerza recarga, devolverla
    if model_type in _f5tts_instances and not force_load:
        print(f"Usando modelo F5TTS en caché: {MODEL_CONFIGS[model_type]['name']} para idioma: {target_lang}")
        return _f5tts_instances[model_type]
    
    print(f"Inicializando modelo F5TTS: {MODEL_CONFIGS[model_type]['name']} para idioma: {target_lang}")
    
    try:
        # Configurar el modelo correcto en el caché
        if not backup_and_restore_model(model_type):
            raise Exception(f"No se pudo configurar el modelo {model_type}")
        
        # Crear nueva instancia
        _f5tts_instances[model_type] = F5TTS()
        
        _is_preloaded = True
        print(f"✅ Modelo {MODEL_CONFIGS[model_type]['name']} cargado correctamente para idioma: {target_lang}")
        return _f5tts_instances[model_type]
        
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
    Función auxiliar para configurar los modelos por primera vez.
    Debe ejecutarse una vez para preparar el sistema.
    """
    print("🔧 Configuración inicial de modelos F5TTS...")
    
    files_info = setup_model_files()
    cache_dir = files_info["cache_dir"]
    original_model = files_info["original_model"]
    spanish_model = files_info["spanish_model"]
    base_backup = files_info["base_backup"]
    
    print(f"\n📁 Directorio de trabajo: {cache_dir}")
    print("Para configurar correctamente el sistema, necesitas:")
    print(f"1. Tu modelo ESPAÑOL debe estar en: {spanish_model}")
    print(f"2. El modelo BASE original estará en: {original_model}")
    print(f"3. Se creará un backup automático en: {base_backup}")
    
    # Verificar estado actual
    print(f"\n📋 Estado actual:")
    print(f"   - Modelo original: {'✅' if original_model.exists() else '❌'} {original_model}")
    print(f"   - Modelo español: {'✅' if spanish_model.exists() else '❌'} {spanish_model}")
    print(f"   - Backup base: {'✅' if base_backup.exists() else '❌'} {base_backup}")
    
    if not spanish_model.exists():
        print(f"\n⚠️  ACCIÓN REQUERIDA:")
        print(f"Copia tu modelo español a: {spanish_model}")
        print(f"Ejemplo: cp tu_modelo_español.safetensors '{spanish_model}'")
        return False
    
    # Si todo está listo, hacer backup inicial
    if original_model.exists() and not base_backup.exists():
        print(f"\n🔄 Creando backup del modelo base original...")
        shutil.copy2(original_model, base_backup)
        print(f"✅ Backup creado en: {base_backup}")
    
    print(f"\n✅ Configuración inicial completada!")
    print(f"Ahora puedes usar get_tts('es') para español y get_tts('en') para inglés")
    return True
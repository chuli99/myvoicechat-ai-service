"""
Módulo para precarga de modelos de IA al iniciar la aplicación.
"""
import time
import torch

def preload_all_models():
    """
    Precarga todos los modelos de IA (whisper, m2m100, f5tts) para evitar
    la carga inicial lenta durante las primeras peticiones.
    """
    start_time = time.time()
    print("Iniciando precarga de modelos...")
    
    # Precarga el modelo Whisper
    print("Precargando modelo Whisper...")
    try:
        from services.whisper_service import load_whisper_model
        whisper_model = load_whisper_model(force_load=True)
        print(f"✅ Modelo Whisper cargado correctamente")
    except Exception as e:
        print(f"❌ Error al cargar el modelo Whisper: {str(e)}")
    
    # Precarga el modelo M2M100
    print("Precargando modelo M2M100...")
    try:
        from services.translation_service import get_translation_model
        m2m_model, m2m_tokenizer, device = get_translation_model(force_load=True)
        print(f"✅ Modelo M2M100 cargado correctamente en {device}")
    except Exception as e:
        print(f"❌ Error al cargar el modelo M2M100: {str(e)}")
    
    # Precarga los modelos F5TTS
    print("Precargando modelos F5TTS...")
    try:
        from services.tts_service import preload_all_models
        preload_all_models()
        print(f"✅ Modelos F5TTS cargados correctamente")
    except Exception as e:
        print(f"❌ Error al cargar los modelos F5TTS: {str(e)}")
    
    total_time = time.time() - start_time
    print(f"✅ Precarga de todos los modelos completada en {total_time:.2f} segundos")
    
    # Devolver True para indicar que todos los modelos están precargados
    return True
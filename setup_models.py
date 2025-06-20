#!/usr/bin/env python3
"""
Script para configurar los modelos F5TTS (español e inglés)
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar servicios
sys.path.append(str(Path(__file__).parent))

from services.tts_service import setup_initial_models, get_cache_directory, setup_model_files

def main():
    print("🎯 Configurador de Modelos F5TTS")
    print("=" * 50)
    
    try:
        # Mostrar información del directorio de caché
        cache_dir = get_cache_directory()
        print(f"📁 Directorio de caché de HuggingFace: {cache_dir}")
        
        # Ejecutar configuración
        success = setup_initial_models()
        
        if success:
            print("\n🎉 ¡Configuración completada exitosamente!")
            print("Ahora puedes ejecutar ./boot.sh para iniciar el servidor")
        else:
            print("\n⚠️  Configuración incompleta")
            print("Sigue las instrucciones mostradas arriba")
            
            # Mostrar comandos específicos
            files_info = setup_model_files()
            spanish_model = files_info["spanish_model"]
            
            print(f"\n💡 Comandos sugeridos:")
            print(f"# Si tienes el modelo español en el directorio actual:")
            print(f"cp modelo_español.safetensors '{spanish_model}'")
            print(f"\n# O navega al directorio y copia manualmente:")
            print(f"cd '{cache_dir}'")
            print(f"# Luego copia tu archivo de modelo español como 'model_spanish.safetensors'")
            
    except Exception as e:
        print(f"❌ Error durante la configuración: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

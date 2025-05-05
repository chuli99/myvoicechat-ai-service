#!/bin/bash

echo "====================================================================="
echo "🚀 Iniciando MyVoiceChat AI Service con precarga de modelos"
echo "====================================================================="

# Directorio del proyecto
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Verifica que esté instalado Python y pip
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado."
    exit 1
fi

# Verifica que las dependencias estén instaladas
echo "📦 Verificando dependencias..."
if ! python3 -c "import importlib; [importlib.import_module(m) for m in ['torch', 'fastapi', 'transformers', 'whisper', 'sentencepiece']]" 2>/dev/null; then
    echo "⚠️ Algunas dependencias no están instaladas. Instalando..."
    pip install -r requirments.txt
fi

# Script de Python para precargar modelos y luego iniciar la aplicación
cat > boot_loader.py << 'EOF'
import asyncio
import uvicorn
from core.preload import preload_all_models

async def main():
    # Precarga todos los modelos
    preload_all_models()
    
    # Inicia la aplicación FastAPI
    print("\n===================================================================")
    print("🌐 Iniciando servidor FastAPI...")
    print("===================================================================\n")
    
    # Inicia el servidor con uvicorn
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Ejecuta el script de precarga
echo "🔄 Iniciando la precarga de modelos y el servidor..."
python3 boot_loader.py

# Si el script termina, muestra un mensaje
echo "👋 Servidor detenido."
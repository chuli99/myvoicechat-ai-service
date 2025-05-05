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

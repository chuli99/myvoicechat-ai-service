from fastapi import FastAPI
from api.tts_route import router as tts_router
from api.whisper_route import router as whisper_router
from api.translation_route import router as translation_router
from api.audio_translation_route import router as translate_audio_router  # Actualizado el nombre del router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title = "MyVoice Ai Service",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:3000"] para mayor seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tts_router)
app.include_router(whisper_router)
app.include_router(translation_router)
app.include_router(translate_audio_router)  # Actualizado el nombre del router

@app.get("/")
async def root():
    return {"message": "Welcome to MyVoice Ai Service!"}
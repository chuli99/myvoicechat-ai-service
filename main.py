from fastapi import FastAPI
from api.tts_route import router as tts_router
from api.whisper_route import router as whisper_router
from api.translation_route import router as translation_router


app = FastAPI(
    title = "MyVoice Ai Service",  # Corregido "tittle" a "title"
    version="1.0.0",
)

app.include_router(tts_router)
app.include_router(whisper_router)
app.include_router(translation_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MyVoice Ai Service!"}
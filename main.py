from fastapi import FastAPI
from api.tts import router as tts_router


app = FastAPI(
    tittle = "MyVoice Ai Service",
    version="1.0.0",
)

app.include_router(tts_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MyVoice Ai Service!"}
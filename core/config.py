from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    f5_tts_cmd: str = "f5-tts_infer-cli"
    f5_tts_model_name: str = "F5TTS_Spanish"  # Modelo predeterminado en ingles y chino
    f5_tts_model_name_es: str = "F5TTS_Spanish" # Modelo en español
    use_gpu: bool = False

    class Config:
        env_file = ".env"
        
settings = Settings()
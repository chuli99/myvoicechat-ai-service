from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    f5_tts_cmd: str = "f5-tts_infer-cli"

    class Config:
        env_file = ".env"
        
settings = Settings()

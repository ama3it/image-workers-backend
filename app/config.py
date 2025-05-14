from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Image task application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

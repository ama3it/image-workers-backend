from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Image task application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
  
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str
    SUPABASE_AUTH_JWKS_URL: str
    SUPABASE_PROJECT_ID: str

    DATABASE_URL: str
    sql_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    class Config:
        env_file = ".env"

settings = Settings()

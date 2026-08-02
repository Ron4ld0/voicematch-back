from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+psycopg://admin:admin_password@localhost:5432/voicematch_db"
    )

    # Segurança
    JWT_SECRET_KEY: str = "your-secret-key-here-please-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Áudio e IA
    AUDIO_UPLOAD_DIR: str = "media/audio"
    OPENAI_API_KEY: Optional[str] = None
    AI_SERVICE_URL: str = "http://localhost:8001"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Shifa Care Clinic Voice Agent"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./clinic.db"
    clinic_timezone: str = "Asia/Karachi"

    cors_origins: list[str] = ["http://localhost:5173"]

    models_dir: str = "models"
    stt_provider: str = "faster_whisper"
    stt_model: str = "base.en"
    tts_provider: str = "piper"
    tts_voice: str = "en_US-lessac-medium"


@lru_cache
def get_settings() -> Settings:
    return Settings()

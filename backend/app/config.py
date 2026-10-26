"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Shifa Care Clinic Voice Agent"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./clinic.db"
    clinic_timezone: str = "Asia/Karachi"

    cors_origins: list[str] = ["http://localhost:5173"]

    models_dir: Path = BACKEND_DIR / "models"
    nlu_model_path: Path = BACKEND_DIR / "models" / "nlu.joblib"
    reports_dir: Path = BACKEND_DIR / "reports"
    stt_provider: str = "faster_whisper"
    stt_model: str = "base.en"
    tts_provider: str = "piper"
    tts_voice: str = "en_US-lessac-medium"

    @field_validator("models_dir", "nlu_model_path", "reports_dir")
    @classmethod
    def _relative_to_backend(cls, value: Path) -> Path:
        return value if value.is_absolute() else BACKEND_DIR / value


@lru_cache
def get_settings() -> Settings:
    return Settings()

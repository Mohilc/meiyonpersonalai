"""Configuration and settings for Personal AI Manager."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    APP_NAME: str = "Personal AI Manager"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Storage
    DB_PATH: Path = DATA_DIR / "manager.db"
    BACKUP_DIR: Path = DATA_DIR / "backups"
    
    # Timezone & Regional Defaults
    TIMEZONE: str = "Asia/Kolkata"
    
    # Autonomy Mode: ASSISTED (Mode A), SUPERVISED (Mode B), RESTRICTED_AUTONOMY (Mode C)
    AUTONOMY_MODE: str = "ASSISTED"
    
    # AI Provider Defaults (pluggable)
    AI_PROVIDER: str = "local_heuristic"  # Can be gemini, ollama, openai, etc.
    AI_API_KEY: str = ""
    AI_MODEL: str = "default"

settings = Settings()
settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

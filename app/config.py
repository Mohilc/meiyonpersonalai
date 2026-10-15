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

    # MCP (Model Context Protocol) Settings
    GMAIL_MCP_ENABLED: bool = True
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""  # 16-character Google App Password
    GMAIL_CREDENTIALS_PATH: str = ""  # Optional path to OAuth credentials.json
    
    LINKEDIN_MCP_ENABLED: bool = True
    LINKEDIN_LI_AT_COOKIE: str = ""  # li_at cookie for authenticated browser session
    LINKEDIN_HEADLESS: bool = True
    MCP_SIMULATION_FALLBACK: bool = True  # Safely simulate when live credentials not yet set

settings = Settings()
settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)


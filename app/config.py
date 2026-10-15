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
    AI_PROVIDER: str = "nvidia_nim"  # nvidia_nim, gemini, ollama, local_heuristic
    AI_API_KEY: str = ""
    AI_MODEL: str = "meta/muse-glimmer-30b"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # Multi-Model Pool
    NVIDIA_REASONING_KEY: str = ""
    NVIDIA_REASONING_MODEL: str = "nvidia/nemotron-3.5-lightning-30b-a3b"

    NVIDIA_GENERAL_KEY: str = ""
    NVIDIA_GENERAL_MODEL: str = "meta/muse-glimmer-30b"

    NVIDIA_VISION_KEY: str = ""
    NVIDIA_VISION_MODEL: str = "google/diffusiongemma-26b-a4b-it"

    GEMINI_API_KEY: str = ""

    # MCP (Model Context Protocol) Settings
    GMAIL_MCP_ENABLED: bool = True
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""  # 16-character Google App Password
    GMAIL_CREDENTIALS_PATH: str = ""  # Optional path to OAuth credentials.json
    
    LINKEDIN_MCP_ENABLED: bool = True
    LINKEDIN_LI_AT_COOKIE: str = ""  # li_at cookie for authenticated browser session
    LINKEDIN_HEADLESS: bool = True
    MCP_SIMULATION_FALLBACK: bool = True  # Safely simulate when live credentials not yet set

    # Messaging Integrations: Telegram & WhatsApp
    TELEGRAM_ENABLED: bool = True
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALLOWED_CHAT_ID: str = ""  # Restrict to user's chat ID for security

    WHATSAPP_ENABLED: bool = True
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"  # Default Twilio Sandbox
    WHATSAPP_ALLOWED_NUMBER: str = ""  # Restrict to user's phone number

settings = Settings()
settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)


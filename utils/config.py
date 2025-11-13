from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = BASE_DIR / ".env"
FALLBACK_ENV_FILE = BASE_DIR / ".env.example"
DEFAULT_BOT_TOKEN = "7966124488:AAHLBrB13H4dKHQ-_DwL97Q8H_05WhVSSxA"
DEFAULT_DATABASE_URL = ""
DEFAULT_BACKEND_URL = "https://mcverify.up.railway.app"
DEFAULT_REVERIFY_DAYS = 3

# Load environment variables from .env first, falling back to .env.example for defaults.
load_dotenv(DEFAULT_ENV_FILE, override=True)
if FALLBACK_ENV_FILE.exists():
    load_dotenv(FALLBACK_ENV_FILE, override=False)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    reverify_days: int
    backend_url: str


@lru_cache
def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", DEFAULT_BOT_TOKEN).strip()
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL).strip()
    backend_url = os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).strip()
    reverify_days = int(os.getenv("REVERIFY_DAYS", str(DEFAULT_REVERIFY_DAYS)))

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        backend_url=backend_url,
        reverify_days=reverify_days,
    )

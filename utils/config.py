from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    reverify_days: int
    backend_url: str


@lru_cache
def get_settings() -> Settings:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    database_url = os.getenv("DATABASE_URL", "").strip()
    backend_url = os.getenv(
        "BACKEND_URL",
        "https://mcverify.up.railway.app",
    ).strip()
    reverify_days = int(os.getenv("REVERIFY_DAYS", "3"))

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not configured")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        backend_url=backend_url,
        reverify_days=reverify_days,
    )

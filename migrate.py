from __future__ import annotations

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

LOGGER = logging.getLogger("migrate")


def _load_config() -> Config | None:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        LOGGER.warning("DATABASE_URL is not set; skipping automatic migrations.")
        return None

    ini_path = Path(__file__).resolve().parent / "alembic.ini"
    if not ini_path.exists():
        LOGGER.warning("alembic.ini not found at %s; skipping automatic migrations.", ini_path)
        return None

    alembic_cfg = Config(str(ini_path))
    alembic_cfg.attributes["configure_logger"] = False
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    return alembic_cfg


def run() -> None:
    """Apply all pending Alembic migrations."""
    cfg = _load_config()
    if cfg is None:
        return

    try:
        command.upgrade(cfg, "head")
        LOGGER.info("Database migrations are up to date.")
    except Exception:
        LOGGER.exception("Failed to apply database migrations.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()

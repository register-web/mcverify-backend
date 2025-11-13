from __future__ import annotations

import os
import logging

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run() -> None:
    """Run Alembic migrations programmatically."""

    try:
        # путь к alembic.ini
        alembic_ini = os.path.join(os.path.dirname(__file__), "alembic.ini")

        alembic_cfg = Config(alembic_ini)

        # Важно: пробрасываем DATABASE_URL в Alembic
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL is not set, migrations skipped")
            return

        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        logger.info("Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")

    except Exception as exc:
        logger.exception("Migration failed: %s", exc)
        raise

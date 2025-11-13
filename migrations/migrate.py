import os
import logging
from alembic import command
from alembic.config import Config

logger = logging.getLogger("migrate")


def run():
    """
    Runs Alembic migrations (upgrade head).

    - Loads alembic.ini
    - Injects DATABASE_URL dynamically
    - Safe to call multiple times (no crash if already upgraded)
    """
    alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")

    if not os.path.exists(alembic_ini_path):
        logger.warning("alembic.ini not found — skipping migrations.")
        return

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL is missing — skipping migrations.")
        return

    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    logger.info("Applying database migrations...")

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Error applying migrations: {e}")
        raise

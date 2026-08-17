import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

logger = logging.getLogger("policypilot.database")

from app.core.settings import settings

db_url = settings.DATABASE_URL or "sqlite:///./storage/policypilot.db"

def _init_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        os.makedirs("./storage", exist_ok=True)
        connect_args["check_same_thread"] = False
        return create_engine(url, connect_args=connect_args)
    else:
        return create_engine(url, pool_pre_ping=True)

try:
    engine = _init_engine(db_url)
    with engine.connect() as conn:
        pass
except (OperationalError, Exception) as err:
    if not db_url.startswith("sqlite"):
        logger.warning(
            f"Database connection to {db_url} failed ({err}). Falling back to SQLite database (sqlite:///./storage/policypilot.db)."
        )
        db_url = "sqlite:///./storage/policypilot.db"
        engine = _init_engine(db_url)
    else:
        raise err
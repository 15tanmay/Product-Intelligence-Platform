import sqlite3
from config.settings import DB_PATH, SCHEMA_PATH
from app_logging.logger import get_logger

logger = get_logger(__name__)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def initialize_database() -> None:
    logger.info("Initializing database...")
    if not SCHEMA_PATH.exists():
        logger.error(f"Schema not found: {SCHEMA_PATH}")
        return
    
    with get_connection() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
    logger.info("Database initialized successfully.")

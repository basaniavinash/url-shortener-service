import os

DB_URL = os.getenv("DB_URL", "sqlite:///./local.db")
SQL_ECHO = bool(int(os.getenv("SQL_ECHO", "0")))
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "5"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "10"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "1800"))  # seconds

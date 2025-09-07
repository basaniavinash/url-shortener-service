import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DB_URL = os.getenv("DB_URL", "postgresql+psycopg://dev:devpass@localhost:5432/urlshortener")
ID_LENGTH = os.getenv("ID_LENGTH", 7)
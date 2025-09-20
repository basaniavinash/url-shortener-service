from contextlib import contextmanager
from select import select
from typing import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_URL, SQL_ECHO, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE
from app.models import Base, ShortUrlRow

engine = create_engine(
    DB_URL,
    echo=SQL_ECHO,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=POOL_RECYCLE,
    connect_args={},  # psycopg2 usually fine empty
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def repo_get(id_: str):
    with session_scope() as s:
        row = s.get(ShortUrlRow, id_)
        return row

def repo_exists(id_: str):
    with session_scope() as s:
        return s.get(ShortUrlRow, id_) is not None

def repo_create(row: ShortUrlRow):
    with session_scope() as s:
        s.add(row)

def repo_update(new_long_url: str, id_: str) -> bool:
    with session_scope() as s:
        row = s.get(ShortUrlRow, id_)
        if not row:
            return False
        row.long_url = new_long_url
        return True

def repo_deactivate(id_: str) -> bool:
    with session_scope() as s:
        row = s.get(ShortUrlRow, id_)
        if not row:
            return False
        row.is_active = False
        return True

def repo_list_by_owner(owner_id: str, limit: int = 50) -> Iterable[ShortUrlRow]:
    with session_scope() as s:
        stmt = (
            select(ShortUrlRow)
            .where(ShortUrlRow.owner_id == owner_id)
            .order_by(ShortUrlRow.created_at.desc())
            .limit(limit)
        )

        return [r for (r,) in s.execute(stmt).all()]


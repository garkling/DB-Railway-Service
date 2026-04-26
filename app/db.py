from collections.abc import Iterator

from sqlalchemy import Connection, Engine, create_engine

from app.config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.DEBUG,
        )
    return _engine


def get_connection() -> Iterator[Connection]:
    with get_engine().connect() as conn:
        yield conn
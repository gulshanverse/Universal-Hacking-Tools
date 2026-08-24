"""SQLAlchemy session boundary for Phase 8 private application state."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings


class DatabaseUnavailable(RuntimeError):
    """Raised when private application-state storage cannot be used safely."""


_engine: Engine | None = None
_factory: sessionmaker[Session] | None = None
_url: str | None = None


def _build(url: str) -> tuple[Engine, sessionmaker[Session]]:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    options = {"future": True, "pool_pre_ping": True, "connect_args": connect_args}
    if not url.startswith("sqlite"):
        config = settings()
        options.update({"pool_size": config.database_pool_size, "max_overflow": config.database_max_overflow, "pool_timeout": config.database_pool_timeout_seconds})
    engine = create_engine(url, **options)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(connection, _record) -> None:
            connection.execute("PRAGMA foreign_keys=ON")
    elif url.startswith("postgresql"):
        statement_timeout = settings().database_statement_timeout_ms

        @event.listens_for(engine, "connect")
        def set_postgresql_statement_timeout(connection, _record) -> None:
            cursor = connection.cursor()
            try:
                cursor.execute(f"SET statement_timeout = {statement_timeout}")
            finally:
                cursor.close()
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def configure_database(url: str | None = None) -> None:
    """Reset the lazy engine; tests use this with an isolated database URL."""
    global _engine, _factory, _url
    if _engine is not None:
        _engine.dispose()
    _engine = _factory = None
    _url = url


def engine() -> Engine:
    global _engine, _factory
    url = _url or settings().database_url
    if _engine is None:
        _engine, _factory = _build(url)
    return _engine


def sessions() -> sessionmaker[Session]:
    engine()
    assert _factory is not None
    return _factory


def database_ready() -> bool:
    try:
        with engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator[Session, None, None]:
    if not database_ready():
        raise HTTPException(status_code=503, detail="private application state is temporarily unavailable")
    session = sessions()()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def transaction() -> Generator[Session, None, None]:
    if not database_ready():
        raise DatabaseUnavailable("private application state is temporarily unavailable")
    session = sessions()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

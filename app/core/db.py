# app/core/db.py
"""
Database configuration and session management.

This module provides PostgreSQL database connectivity using SQLModel and SQLAlchemy.
Includes proper session management with transaction handling.
"""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import db_activity, frames
from app.core.config import settings
from app.core.constants import ComponentName
from app.core.log import logger

# The component this client fronts (``ownership``, ``ontology.calls``).
FRONTS = ComponentName.DATABASE


def client_url() -> str:
    """The URL pg_dump and psql reach the database at, from where this
    runs (``database_url_effective``)."""
    return settings.database_url_effective


# Create PostgreSQL engine with proper configuration (sync)
engine = create_engine(
    settings.database_url_effective,
    echo=settings.DATABASE_ENGINE_ECHO,
)


# Create async engine for non-blocking operations
def _get_async_database_url(database_url: str) -> str:
    """Convert sync database URL to async version.

    SQLite is handled whatever engine this project runs on: the test suite
    points ``DATABASE_URL`` at a throwaway SQLite file before this module
    builds its engines, so a Postgres project's tests run on SQLite too.
    """
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://")

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

        return database_url

    # For other database types, return as-is and let SQLAlchemy handle it
    return database_url


async_engine = create_async_engine(
    _get_async_database_url(settings.database_url_effective),
    echo=settings.DATABASE_ENGINE_ECHO,
)


# Long-held transactions and lock failures, for the Database pages.
db_activity.watch(engine)
db_activity.watch(async_engine.sync_engine)


# Each connection names the process that opened it, as pg_stat_activity
# shows it (the Database page's Transactions). Set as it connects, not at
# import, so a forked process names itself.
@event.listens_for(engine, "do_connect")
@event.listens_for(async_engine.sync_engine, "do_connect")
def _name_connection(
    dialect: Any, conn_rec: Any, cargs: Any, cparams: dict[str, Any]
) -> None:
    """psycopg takes it as a connect argument, asyncpg as a server setting."""
    name = frames.process()
    if dialect.is_async:
        cparams.setdefault("server_settings", {})["application_name"] = name
    else:
        cparams["application_name"] = name


# Configure session factory with SQLModel Session (sync)
SessionLocal = sessionmaker(
    class_=Session, bind=engine, autoflush=False, autocommit=False
)

# Configure async session factory using SQLModel's AsyncSession
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@contextmanager
def db_session(autocommit: bool = True) -> Generator[Session]:
    """
    Database session context manager with automatic transaction handling.

    Args:
        autocommit: Whether to automatically commit the transaction on success

    Yields:
        Session: Database session instance

    Example:
        with db_session() as session:
            # Your database operations here
            result = session.query(MyModel).first()
    """
    db_session: Session = SessionLocal()
    try:
        yield db_session
        if autocommit:
            db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """
    Async database session context manager with automatic transaction handling.

    Yields:
        AsyncSession: Async database session instance

    Example:
        async with get_async_session() as session:
            # Your async database operations here
            result = await session.exec(select(MyModel))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await _purge_released(session)


async def release_lock(session: AsyncSession) -> None:
    """Commit, ending ``session``'s transaction before slow work that needs
    no database (a model call, a fetch over the network) or before code
    that opens a connection of its own; its next query begins a new one.
    On SQLite a transaction holds the one write lock from its first query
    (the async engine begins IMMEDIATE): one left open across a model that
    takes minutes stalls every process, and a second connection the same
    request opens waits out the busy timeout behind it. On Postgres it is
    a connection idle in a transaction."""
    await session.commit()


async def _purge_released(session: AsyncSession) -> None:
    """Delete what the transaction just committed released
    (``app.components.database.stored``): every caller's session ends here,
    so none has to remember to. A purge that fails leaves the objects
    marked, and the next one deletes them."""
    if not session.info.pop("released", False):
        return
    from app.components.database.stored import purge

    try:
        await purge(session)
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("The storage purge failed; the next one will retry")


def insert(session: AsyncSession, model: Any) -> Any:
    """The INSERT for ``session``'s database that can take an ``ON CONFLICT``
    (upsert, or do nothing): each dialect spells it under its own ``insert``."""
    from sqlalchemy.dialects import postgresql, sqlite

    name = session.sync_session.get_bind().dialect.name
    return (postgresql if name == "postgresql" else sqlite).insert(model)


def init_database() -> None:
    """
    Initialize the database (no-op for postgres - use migrations).


    For PostgreSQL, this is a no-op. Use Alembic migrations to create/modify tables.
    This function exists for SQLite compatibility where CLI commands need tables
    to exist without running migrations.

    """

    # PostgreSQL uses Alembic migrations - create_all() would conflict
    # This no-op exists so code calling init_database() still works
    pass


# ---------------------------------------------------------------------
# FastAPI-flavored session generators
#
# These live with the engine factories rather than under
# ``app/components/backend/api/deps.py`` so per-service deps modules
# (``app.services.<svc>.deps``) can import them without going through
# the api shim — the api shim imports BACK from the per-service deps,
# which would otherwise be a circular import.
#
# The functions are plain generators; FastAPI consumers wire them via
# ``Depends(get_async_db)`` at the call site.
# ---------------------------------------------------------------------


def get_db() -> Generator[Session]:
    """Yield a synchronous SQLModel session, closing it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession]:
    """Yield an async SQLModel session, committing on success and rolling
    back on any exception."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await _purge_released(session)

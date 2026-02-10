# app/core/db.py
"""
Database configuration and session management.

This module provides PostgreSQL database connectivity using SQLModel and SQLAlchemy.
Includes proper session management with transaction handling.
"""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from typing import Any


from sqlalchemy import create_engine

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.log import logger




# Create PostgreSQL engine with proper configuration (sync)
engine = create_engine(
    settings.database_url_effective,
    echo=settings.DATABASE_ENGINE_ECHO,
)


# Create async engine for non-blocking operations
def _get_async_database_url(database_url: str) -> str:
    """Convert sync database URL to async version."""

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://")

    # For other database types, return as-is and let SQLAlchemy handle it
    return database_url


async_engine = create_async_engine(
    _get_async_database_url(settings.database_url_effective),
    echo=settings.DATABASE_ENGINE_ECHO,
)



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
def db_session(autocommit: bool = True) -> Generator[Session, None, None]:
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
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
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


"""
Pytest configuration and fixtures for test suite.

Provides common fixtures and configuration for all tests.
"""

from collections.abc import AsyncGenerator, Callable, Generator
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

# Before any app import reads settings: a developer .env with a real
# LOGFIRE_TOKEN must never arm instrumentation (or ship test spans).
os.environ["LOGFIRE_TOKEN"] = ""

# Same window, same reason: ``app.core.db`` builds its engine at import
# from ``DATABASE_URL``, and DDL goes through that engine rather than
# through the session factories the fixtures redirect. Point it at a
# throwaway file HERE so no window is left open - not import time, not a
# fixture teardown after monkeypatch has reverted, not an atexit hook.
# ``create_all`` only ever ADDS tables, so the damage was never data: it
# was a table frozen at the models' shape in that moment, in a developer's
# live database, that nothing would ever correct.
os.environ["DATABASE_URL"] = (
    f"sqlite:///{tempfile.mkdtemp(prefix='aegis-test-db-')}/app.db"
)
# And every setting the app prefers over it: ``.env``'s
# ``DATABASE_URL_LOCAL`` on the host, ``DATABASE_URL_UNPOOLED`` (alembic's,
# on Neon). Left set, each test entering the app's lifespan runs startup
# migrations - stamp, upgrade - against the developer's real database.
os.environ["DATABASE_URL_LOCAL"] = ""
os.environ["DATABASE_URL_UNPOOLED"] = ""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest  # noqa: E402
from sqlalchemy import create_engine, event
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Import scheduler models to register them with SQLModel metadata


# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.model_registry import import_all_models  # noqa: E402
from app.integrations.main import create_integrated_app

import_all_models()

# queryspy's baseline knows a repeated statement by its shape, so a new
# column does not turn every known entry into a new one.
from tests import _queryspy_shape  # noqa: E402
from tests._files import forget  # noqa: E402

# ``--shard K/N`` for CI's parallel test jobs; importing the hooks registers them.
from tests._shard import (  # noqa: E402, F401
    pytest_addoption,
    pytest_collection_modifyitems,
)


def pytest_sessionstart(session: pytest.Session) -> None:
    # After every plugin's pytest_configure, so queryspy has read the file.
    _queryspy_shape.shape_loaded_baseline(session.config)


# Swap the module-level ``cache`` singleton to the in-memory dict
# backend for the whole test session. The Redis-backed singleton
# binds its async connection pool to the event loop alive when it
# was constructed (at import time). pytest-asyncio creates a fresh
# loop for every test, so the first test's Redis client becomes
# unusable for every subsequent test. Production isn't affected
# (uvicorn keeps one loop for the server's lifetime); only the
# test suite needs this swap. Dict-mode keeps the same async API,
# so call sites don't change.
@pytest.fixture
def fake_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Callable[..., Path]]:
    """Make a service package on ``app.services``' path, as a plugin would:
    ``fake_service("demo_x", scheduled_jobs="JOBS = ()")`` writes
    ``demo_x/scheduled_jobs.py``. For the conventions found on disk
    (``app.core.discovery``); the modules it imported are forgotten after."""
    import app.services as services

    monkeypatch.setattr(services, "__path__", [*services.__path__, str(tmp_path)])
    made: list[str] = []

    def make(name: str, **modules: str) -> Path:
        package = tmp_path / name
        package.mkdir()
        (package / "__init__.py").write_text("")
        for module, source in modules.items():
            (package / f"{module}.py").write_text(source)
        made.append(f"app.services.{name}")
        return package

    yield make
    forget(*made)


@pytest.fixture
def clean_registry() -> Generator[None]:
    """Unregister the tools a test registered, so cases stay independent.

    Opt-in, never autouse: a module first imported during a test registers
    its tools then, and unregistering them would leave the cached module's
    tools missing for every later test."""
    from app.core.tools import registered_tool_names, unregister_tool

    before = set(registered_tool_names())
    yield
    for name in set(registered_tool_names()) - before:
        unregister_tool(name)


@pytest.fixture(autouse=True)
def _fresh_system_status_cache():
    """No test sees another test's cached system-status walk."""
    from app.services.system.health import invalidate_status_cache

    invalidate_status_cache()
    yield


@pytest.fixture(autouse=True)
def _no_background_sampling(monkeypatch: pytest.MonkeyPatch) -> None:
    """The live charts' samplers (``app.core.series``) poll Docker and
    Ollama: an app started in a test samples nothing, and each test's
    sampled history starts empty."""
    from app.core import series
    from app.core.cache import CacheService
    from app.core.series_store import SeriesStore

    async def idle(samplers: Any) -> None:
        return None

    from app.core.config import settings

    monkeypatch.setattr(settings, "ERROR_TRACKING_ENABLED", False)
    cache, history = CacheService(), SeriesStore()
    monkeypatch.setattr(series, "run", idle)
    monkeypatch.setattr(series, "get_cache", lambda: cache)
    monkeypatch.setattr(series, "get_store", lambda: history)


@pytest.fixture(autouse=True)
def _no_load_cost_measuring(monkeypatch: pytest.MonkeyPatch) -> None:
    """A page asking what each part costs to load (``load_cost``) starts
    measuring in the background, a Python per part: no test starts one."""
    from app.services.system import load_cost

    monkeypatch.setattr(load_cost, "_start", lambda: None)


@pytest.fixture
def run_log_sink() -> Generator[Any]:
    """A run log of this test's own (``run_log.MemorySink``), put back after."""
    from app.core import run_log

    previous = run_log.sink()
    memory = run_log.MemorySink()
    run_log.use(memory)
    yield memory
    run_log.use(previous)


@pytest.fixture
async def store() -> AsyncGenerator[Any]:
    """The error store's Lua against a real Redis, only when one is named:
    the suite never writes to the developer's running Redis. Point
    ``AEGIS_ERROR_TRACKING_REDIS_URL`` at a throwaway one
    (``docker run --rm -p 6390:6379 redis``); each test gets a namespace."""
    from uuid import uuid4

    from app.services.system.errors.store import ErrorStore

    url = os.environ.get("AEGIS_ERROR_TRACKING_REDIS_URL")
    if not url:
        pytest.skip("Set AEGIS_ERROR_TRACKING_REDIS_URL to a throwaway Redis to run")
    redis = pytest.importorskip("redis.asyncio")
    client = redis.from_url(url, socket_connect_timeout=1)
    repository = ErrorStore(
        client,
        "test-" + uuid4().hex,
        max_occurrences=3,
        retention_seconds=7 * 86400,
        max_bytes=1 << 20,
    )
    yield repository
    keys = [key async for key in client.scan_iter(repository.prefix + "*")]
    await client.delete(repository.notifications, *keys)
    await client.aclose()


@pytest.fixture(autouse=True, scope="session")
def _no_real_redis():
    """Every Redis the app builds at import or startup, held in memory for
    the session. Each is at ``redis_url_effective``, which on the host is
    the running dev stack's Redis: tests would count into its traffic
    panel and attach the job API to its store. The cache also binds to an
    event loop at import, and each test gets a fresh one. The job store's
    stand-in is one in-memory Redis, as one server would be."""
    from app.components.backend.middleware import traffic
    from app.core import run_log
    import app.core.cache as cache_module
    from app.services.system.job_store import RedisJobStore
    from tests._fake_redis import FakeRedis

    memory = FakeRedis()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cache_module, "cache", cache_module.CacheService())
        patch.setattr(traffic, "traffic_monitor", traffic.TrafficMonitor())
        patch.setattr(
            RedisJobStore, "from_url", classmethod(lambda cls, _url: cls(memory))
        )
        # The run log stays in this process (``run_log_sink`` for a test's own).
        patch.setattr(run_log, "attach_redis", lambda *_args, **_kwargs: None)
        yield


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """The configured FastAPI app, built once for the whole session.

    ``create_integrated_app()`` wires every router, middleware and startup
    hook; per test that is the single most expensive thing a suite does.
    Nothing is read from mutable settings at build time, and ``TestClient``
    still runs the lifespan per context manager, so one instance is safe
    to share.

    Sharing it does mean ``app.dependency_overrides`` outlives a test;
    ``_clear_dependency_overrides`` below is what keeps that from leaking.
    """
    return create_integrated_app()


@pytest.fixture(autouse=True)
def _clear_dependency_overrides(app: FastAPI) -> Generator[None]:
    """Hand every test a clean override table.

    With a session-scoped app, an override a test forgets to pop (or one
    left behind by a failing test) is inherited by everything that runs
    after it, which shows up as order-dependent failures far from the
    cause. Clearing on both sides makes that impossible.
    """
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def files(tmp_path: Path) -> Generator[Any]:
    """The object store (``app.core.storage``), on disk in the test's own
    directory and put back after it."""
    from app.core.storage import FilesystemStorage, set_storage

    store = FilesystemStorage(tmp_path)
    set_storage(store)
    yield store
    set_storage(None)


@pytest.fixture
def client_with_db(app: FastAPI, db_session: Session) -> Generator[TestClient]:
    """Create a test client with database dependency override."""
    from app.core.db import get_db

    def get_test_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def engine() -> Engine:
    """
    Create in-memory SQLite database engine for tests.

    Uses :memory: database that exists only in RAM for maximum speed
    and perfect test isolation. Each test session gets a fresh database.

    Returns:
        SQLAlchemy Engine connected to in-memory SQLite database
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False},  # Allow multi-threaded access
    )

    # Non-default schemas our models declare (e.g. the scheduler component's
    # ``scheduler`` schema on Postgres projects). SQLite has no schemas, so
    # attach an in-memory database under each name to make schema-qualified
    # tables resolvable in the test database.
    schema_names = {
        table.schema for table in SQLModel.metadata.tables.values() if table.schema
    }

    # Critical: Enable foreign key constraints in SQLite
    # SQLite has foreign keys disabled by default for backwards compatibility
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        for schema_name in schema_names:
            cursor.execute(f"ATTACH DATABASE ':memory:' AS {schema_name}")
        cursor.close()

    # Create all tables once per test session
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture(scope="function")
def db_session(engine: Engine) -> Generator[Session]:
    """
    Provide transactional database session with automatic rollback.

    Each test gets a fresh transaction that's rolled back after the test,
    ensuring perfect isolation between tests. Uses the same transaction
    pattern as PostgreSQL for consistency.

    Args:
        engine: Database engine from session-scoped fixture

    Yields:
        SQLModel Session for database operations
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(connection)

    yield session

    # Clean up: rollback transaction and close connection
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
async def app_owned_engine():
    """A database for sessions the APP opens for itself.

    Deliberately not ``async_engine``: that one is wrapped in a per-test
    transaction which is rolled back, and app-owned sessions commit. Put
    both on one connection and they fight over the same transaction.

    File-backed, not ``:memory:``. TestClient runs the app in its OWN
    event loop on a separate thread, so app-owned sessions reach this
    engine from a different thread than the one that built it. Every new
    connection to ``:memory:`` is a BRAND NEW EMPTY database, so a
    reconnect there loses every table - which surfaces much later as
    "no such table: agent", and only in long runs, because a short one
    never reconnects. A file is the same database from any thread.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="aegis-app-owned-db-"))
    schema_names = {
        table.schema for table in SQLModel.metadata.tables.values() if table.schema
    }
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_dir / 'app_owned.sqlite'}",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def attach_schemas(dbapi_connection: Any, connection_record: Any) -> None:
        dbapi_connection.isolation_level = None
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # Files here too, for the same reason the main database is one.
        for schema_name in schema_names:
            cursor.execute(
                f"ATTACH DATABASE '{tmp_dir / (schema_name + '.sqlite')}' "
                f"AS {schema_name}"
            )
        cursor.close()

    # Production is Postgres, whose MVCC this engine cannot imitate; a
    # plain BEGIN is the nearer of the two SQLite shapes.
    @event.listens_for(engine.sync_engine, "begin")
    def emit_begin(conn: Any) -> None:
        conn.exec_driver_sql("BEGIN")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    await engine.dispose()
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def _no_production_database(app_owned_engine, monkeypatch):
    """Keep app-owned sessions off the real database.

    ``get_async_session()`` reads a module-level ``AsyncSessionLocal``.
    Overriding the FastAPI dependency does not touch it, so every caller
    that opens its own session - startup hooks, background tasks,
    ``resolve_agent()`` inside a chat - was talking to the database in
    ``DATABASE_URL`` while the suite ran.

    Two consequences. Tests read and write live data. And the production
    engine POOLS asyncpg connections, which pytest then hands to a fresh
    event loop each test; using a connection from a loop that did not
    create it raises "another operation is in progress" - failing tests
    that never touched the database themselves, only in a full run, and
    never in isolation.
    """
    import app.core.db as db_module

    monkeypatch.setattr(
        db_module,
        "AsyncSessionLocal",
        async_sessionmaker(
            app_owned_engine, class_=AsyncSession, expire_on_commit=False
        ),
    )
    # The sync factory too: ``db_session()`` is what startup hooks and the
    # scheduler still open for themselves (the chat store is async). A sync
    # engine on the SAME file, with the same schema attachments, so both
    # factories see one database - the one ``app_owned_engine`` already
    # ran ``create_all`` on.
    # Left uncovered, a Postgres project fails "no such table" on the first
    # sync lookup: its startup migrations begin with CREATE SCHEMA, which
    # SQLite rejects, so nothing else ever creates tables for that path.
    owned_db = Path(app_owned_engine.url.database)
    schema_names = {
        table.schema for table in SQLModel.metadata.tables.values() if table.schema
    }
    sync_engine = create_engine(
        f"sqlite:///{owned_db}", echo=False, connect_args={"check_same_thread": False}
    )

    @event.listens_for(sync_engine, "connect")
    def attach_schemas_sync(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        for schema_name in schema_names:
            cursor.execute(
                f"ATTACH DATABASE '{owned_db.parent / (schema_name + '.sqlite')}' "
                f"AS {schema_name}"
            )
        cursor.close()

    monkeypatch.setattr(
        db_module,
        "SessionLocal",
        sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False),
    )
    yield
    sync_engine.dispose()


@pytest.fixture(scope="session")
async def async_engine():
    """
    Create async in-memory SQLite database engine for async tests.

    Uses :memory: database that exists only in RAM for maximum speed
    and perfect test isolation. Each test session gets a fresh database.

    Returns:
        Async SQLAlchemy Engine connected to in-memory SQLite database
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False},  # Allow multi-threaded access
    )

    # Attach an in-memory database for each non-default schema our models use
    # (mirrors the sync ``engine`` fixture). SQLite has no schemas, so without
    # this, create_all of a schema-qualified table (e.g. scheduler.job_execution
    # on Postgres projects) fails.
    schema_names = {
        table.schema for table in SQLModel.metadata.tables.values() if table.schema
    }

    @event.listens_for(engine.sync_engine, "connect")
    def attach_schemas(dbapi_connection: Any, connection_record: Any) -> None:
        # Match production transaction handling: pysqlite's implicit
        # BEGIN/COMMIT sniffing commits the open transaction before SAVEPOINT,
        # which both breaks begin_nested() semantics and leaks rows across the
        # per-test rollback isolation. Take over transaction control (paired
        # with the "begin" listener below).
        dbapi_connection.isolation_level = None
        cursor = dbapi_connection.cursor()
        # Match the sync engine: enforce foreign keys so async tests catch
        # FK violations that would otherwise pass here but fail in production.
        cursor.execute("PRAGMA foreign_keys=ON")
        for schema_name in schema_names:
            cursor.execute(f"ATTACH DATABASE ':memory:' AS {schema_name}")
        cursor.close()

    @event.listens_for(engine.sync_engine, "begin")
    def emit_begin(conn: Any) -> None:
        conn.exec_driver_sql("BEGIN")

    # Create all tables once per test session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_db_session(async_engine) -> AsyncGenerator[AsyncSession]:
    """
    Provide async transactional database session with automatic rollback.

    Each test gets a fresh transaction that's rolled back after the test,
    ensuring perfect isolation between tests. Uses async SQLite with aiosqlite.

    Args:
        async_engine: Async database engine from session-scoped fixture

    Yields:
        AsyncSession: SQLModel async session for database operations
    """
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection, class_=AsyncSession, expire_on_commit=False
        )

        async with session_factory() as session:
            yield session

        # Clean up: rollback transaction
        await transaction.rollback()


@pytest.fixture
async def key_holder(async_db_session: AsyncSession) -> AsyncGenerator[Any]:
    """A table naming stored objects the two ways rows do (``app.core.storage``):
    a ``*_key`` column (a document's file) and inside JSON (a chat
    attachment), beside a ``*_key`` that names something else."""
    from sqlalchemy import JSON, Column, Integer, String, Table
    from sqlmodel import AutoString

    table = Table(
        "key_holder",
        SQLModel.metadata,
        Column("id", Integer, primary_key=True),
        Column("file_key", AutoString),
        Column("payee_key", String),
        Column("meta_data", JSON),
    )
    await async_db_session.run_sync(lambda s: table.create(s.connection()))
    yield table
    SQLModel.metadata.remove(table)


@pytest.fixture
async def async_client_with_db(
    app: FastAPI, async_db_session: AsyncSession
) -> AsyncGenerator[TestClient]:
    """Create a test client with async database dependency override."""
    from app.core.db import get_async_db

    async def get_test_async_db() -> AsyncGenerator[AsyncSession]:
        yield async_db_session

    app.dependency_overrides[get_async_db] = get_test_async_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(
    async_client_with_db: TestClient,
    auth_headers: dict[str, str],
) -> TestClient:
    """``async_client_with_db`` with ``auth_headers`` pre-injected.

    Use this when a test needs "an authenticated request, don't care
    who" — write ``authenticated_client.get(url)`` instead of plumbing
    ``headers={"Authorization": ...}`` on every call. Eliminates the
    per-request boilerplate without hiding which user is acting (the
    seeded ``auth_user`` / ``admin_user`` is the actor).

    Auth-mode behavior:

    - ``include_auth_rbac``: signs requests as ``admin_user``.
    - ``include_auth``: signs requests as ``auth_user``.
    - no auth: ``auth_headers`` is ``{}``; this fixture is a passthrough.

    For tests that need multiple distinct identities or want to pin a
    specific user / role, skip this and compose ``user_factory`` +
    ``create_access_token`` inline so the identity choice is visible.
    """
    async_client_with_db.headers.update(auth_headers)
    return async_client_with_db


# ---------------------------------------------------------------------------
# Auth headers fixture chain — kept OUTSIDE the ``include_database`` block
# above so the no-op fallback is available even in stacks without a DB
# (e.g. ``worker``-only). ``test_worker_endpoints.py.jinja`` always asks
# for ``auth_headers``; without this it would error with "fixture not
# found" in DB-less stacks. The RBAC / basic-auth branches still need
# ``async_db_session`` to seed users, which only exists when
# ``include_database`` is true — the template never enables auth without
# a database, so those branches are safe to reference it.
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """No-op headers fixture for stacks without the auth service.

    Tests that share assertions with auth-enabled stacks can ask for
    ``auth_headers`` and get ``{}`` here; the endpoints aren't gated.
    """
    return {}


@pytest.fixture
def acting_owner_user_id() -> int | None:
    """No auth service, so owner-scoped rows carry no owner.

    The auth-stack counterpart returns the authenticated user's id; here
    ``None`` keeps seed helpers written once and correct in both stacks.
    """
    return None


@pytest.fixture
def authenticated_app_client(client: TestClient) -> TestClient:
    """No auth service, so this is ``client`` unchanged.

    Keeps the documents suites written once: they ask for the same
    fixture in both stacks, and only the auth stack has anything to
    sign. See the auth-stack docstring for why it is not
    ``authenticated_client``.
    """
    return client

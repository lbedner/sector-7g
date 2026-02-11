"""
Database initialization startup hook.

Runs Alembic migrations and verifies connectivity
when the backend starts up (only when database component is included).
"""



from app.core.log import logger

# Import models to register them with SQLModel metadata
from app.models.user import User  # noqa: F401


def _check_and_stamp_existing_tables() -> None:
    """
    Detect when tables for a pending migration already exist.

    This handles the case where:
    - Project regenerated with -f flag
    - Docker volume persisted with old tables
    - alembic_version is valid but behind (e.g., at 001 when 002 tables exist)

    Fix: If signature table for a migration exists, stamp it as complete.
    """
    try:
        from sqlalchemy import inspect

        from alembic import command
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from app.core.db import db_session

        alembic_cfg = Config("alembic/alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        # Get existing tables and current revision
        with db_session(autocommit=False) as session:
            inspector = inspect(session.connection())
            existing_tables = set(inspector.get_table_names())

            context = MigrationContext.configure(session.connection())
            current_rev = context.get_current_revision()

        # Signature table for each migration (first table created by that migration)
        signature_tables = {
            "001": "user",        # auth migration
            "002": "llm_vendor",  # ai migration
        }

        # Walk revisions and stamp any with pre-existing tables
        for rev in script.walk_revisions():
            # Skip if already applied
            if current_rev and rev.revision <= current_rev:
                continue

            sig_table = signature_tables.get(rev.revision)
            if sig_table and sig_table in existing_tables:
                logger.warning(
                    f"Migration {rev.revision} tables already exist. "
                    "Stamping as complete (Docker volume likely persisted)..."
                )
                command.stamp(alembic_cfg, rev.revision)
                logger.info(f"Stamped migration {rev.revision}")

    except Exception as e:
        logger.debug(f"Existing tables check skipped: {e}")


def _check_and_fix_stale_revision() -> None:
    """
    Detect and fix stale alembic_version entries.

    This handles the case where project is regenerated with -f flag:
    - Database has old revision ID in alembic_version
    - New migration files have different revision IDs
    - Alembic can't find the old revision and fails

    Fix: If revision doesn't exist in scripts, clear alembic_version
    and stamp to head (tables already exist, just need version sync).
    """
    try:
        from sqlmodel import text

        from alembic import command
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from app.core.db import db_session

        alembic_cfg = Config("alembic/alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        # Get all known revision IDs from migration files
        known_revisions = {rev.revision for rev in script.walk_revisions()}

        # Check current database revision
        with db_session(autocommit=False) as session:
            try:
                result = session.exec(
                    text("SELECT version_num FROM alembic_version")
                )
                db_revisions = [row[0] for row in result.fetchall()]
            except Exception:
                # Table doesn't exist or other error - let migrations handle it
                return

        # Check if any DB revision is stale (not in migration files)
        stale_revisions = [r for r in db_revisions if r not in known_revisions]

        if stale_revisions:
            logger.warning(
                f"Detected stale revisions: {stale_revisions}. "
                "This happens after project regeneration. Auto-recovering..."
            )
            # Clear alembic_version and stamp to head
            with db_session(autocommit=True) as session:
                session.exec(text("DELETE FROM alembic_version"))

            # Stamp to head (marks DB as up-to-date without running migrations)
            command.stamp(alembic_cfg, "head")
            logger.info("Recovery complete: stamped database to head revision")

    except Exception as e:
        logger.debug(f"Stale revision check skipped: {e}")
        # Don't fail - let normal migration flow handle errors


def _run_migrations() -> bool:
    """
    Run Alembic migrations programmatically.

    Returns:
        True if migrations ran successfully, False otherwise.
    """
    try:
        from alembic import command
        from alembic.config import Config

        # Check for stale revisions first (handles -f regeneration)
        _check_and_fix_stale_revision()

        # Check for pre-existing tables (handles persisted Docker volumes)
        _check_and_stamp_existing_tables()

        alembic_cfg = Config("alembic/alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        return False


async def startup_database_init() -> None:
    """
    Initialize database and run migrations.

    This hook runs when the backend starts to:
    1. Verify database connectivity
    2. Run Alembic migrations (idempotent - safe to run multiple times)
    3. Verify database schema is ready

    """
    try:


        # Run Alembic migrations (idempotent)
        migrations_ok = _run_migrations()

        if not migrations_ok:
            logger.warning("Migrations failed - database may not be fully initialized")
            # Continue anyway to allow debugging

        # Verify database connectivity
        try:
            from sqlalchemy import inspect
            from sqlmodel import text

            from app.core.db import db_session

            with db_session(autocommit=False) as session:
                # Basic connectivity check
                session.exec(text("SELECT 1"))

                # Verify alembic_version table exists
                inspector = inspect(session.connection())
                table_names = inspector.get_table_names()

                if "alembic_version" in table_names:
                    logger.info(f"Database ready with {len(table_names)} tables")
                else:
                    logger.warning("alembic_version table missing after migrations")

        except Exception as e:
            logger.warning(f"Database verification failed: {e}")
            # Don't fail startup - let the app run and show clear errors



    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Export the startup hook function
startup_hook = startup_database_init

"""
Database backup service for sector-7g.

Provides database (and object storage) backups for scheduled backup jobs.
Included when scheduler and database components are both present.

Dumps use pg_dump's custom format (``-Fc``): compressed, and restorable
selectively with pg_restore. Plain ``.sql``
dumps written by older versions are still matched for cleanup and restore,
so both formats coexist until the old ones age out.

"""

import asyncio
from datetime import datetime
from pathlib import Path
import subprocess
import tarfile

from app.core.config import settings
from app.core.db import client_url
from app.core.log import logger
from app.core.storage import FilesystemStorage, get_storage

# Backup file naming pattern
BACKUP_FILE_PREFIX = "database_backup_"

BACKUP_FILE_SUFFIX = ".dump"
# Pre-custom-format dumps. Matched so cleanup and restore keep working on
# backups taken before the switch to ``-Fc``.
LEGACY_BACKUP_FILE_SUFFIX = ".sql"
BACKUP_FILE_PATTERNS = (
    f"{BACKUP_FILE_PREFIX}*{BACKUP_FILE_SUFFIX}",
    f"{BACKUP_FILE_PREFIX}*{LEGACY_BACKUP_FILE_SUFFIX}",
)

# Kept for callers that imported the single-pattern name.
BACKUP_FILE_PATTERN = BACKUP_FILE_PATTERNS[0]
# Object storage snapshots, beside the database copies. Not in
# BACKUP_FILE_PATTERNS: those are what a restore lists, and a tarball is
# not a database.
STORAGE_BACKUP_PREFIX = "storage_backup_"
STORAGE_BACKUP_SUFFIX = ".tar"
STORAGE_BACKUP_PATTERNS = (f"{STORAGE_BACKUP_PREFIX}*{STORAGE_BACKUP_SUFFIX}",)


def backup_dir() -> Path:
    """The directory dumps are written to and pruned from.

    Configurable so deployments can point it at a mounted absolute path.
    Left relative it resolves against the process cwd, which inside a
    container is the writable layer: the dumps would then be destroyed by
    the next container recreation, i.e. every deploy.
    """
    return Path(settings.DATABASE_BACKUP_DIR)


def list_backups(
    directory: Path, patterns: tuple[str, ...] = BACKUP_FILE_PATTERNS
) -> list[Path]:
    """Every backup file in ``directory``, newest first, all formats."""
    files = [f for pattern in patterns for f in directory.glob(pattern) if f.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _snapshot_storage(source: Path, destination: Path) -> None:
    """A plain tar of the object store, streamed file by file.

    Not gzipped: the store is mostly PDFs and images, already compressed,
    so gzip would spend the worker's CPU every night to save next to
    nothing.

    Written under a temporary name and renamed when complete, so a run
    that dies halfway never leaves a truncated archive counted as a backup.
    Blocking, so callers run it off the loop.
    """
    partial = destination.with_name(destination.name + ".partial")
    with tarfile.open(partial, "w") as tar:
        tar.add(source, arcname="storage")
    partial.replace(destination)


async def _run_blocking(cmd: list[str]) -> "subprocess.CompletedProcess[str]":
    """pg_dump/psql run for as long as the database is big; in a worker
    thread the event loop (and every other scheduled job) keeps breathing."""
    return await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True)


async def backup_database_job() -> None:
    """
    Scheduled database backup job.


    Creates a compressed backup of the PostgreSQL database using pg_dump.

    Keeps the last ``DATABASE_BACKUP_KEEP`` backups to bound disk usage.
    """
    # Ensure backup directory exists. parents=True because a configured
    # absolute path may be more than one level deep.
    directory = backup_dir()
    directory.mkdir(parents=True, exist_ok=True)

    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{BACKUP_FILE_PREFIX}{timestamp}{BACKUP_FILE_SUFFIX}"
    backup_path = directory / backup_filename

    # Run pg_dump. Raise on failure so the run is recorded as failed instead
    # of a silent "success" that left no usable dump behind.
    try:
        result = await _run_blocking(
            [
                "pg_dump",
                client_url(),
                "-Fc",
                "-f",
                str(backup_path),
            ]
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "pg_dump not found. Install the PostgreSQL client "
            "(postgresql-client), or run this inside the container where a "
            "matching client is available."
        ) from e
    if result.returncode != 0:
        backup_path.unlink(missing_ok=True)  # drop any partial dump
        stderr = result.stderr.strip()
        # pg_dump refuses to dump a server newer than the client.
        if "server version" in stderr:
            stderr += (
                " (the local pg_dump is older than the database server -- run "
                "this inside the container, or upgrade your pg_dump client)"
            )
        raise RuntimeError(f"pg_dump failed: {stderr}")
    logger.info(f"Database backup created: {backup_path}")

    # The documents the rows point at. Only for the filesystem backend: a
    # bucket keeps its own copies, and a store nothing has written to yet
    # has nothing to keep.
    storage_root = Path(settings.STORAGE_ROOT)
    if isinstance(get_storage(), FilesystemStorage) and storage_root.is_dir():
        storage_path = (
            directory / f"{STORAGE_BACKUP_PREFIX}{timestamp}{STORAGE_BACKUP_SUFFIX}"
        )
        await asyncio.to_thread(_snapshot_storage, storage_root, storage_path)
        logger.info(f"Storage backup created: {storage_path}")

    # Prune old backups. Only reached on a successful backup, so a failed
    # run never deletes known-good backups.
    await _cleanup_old_backups(directory)


async def _cleanup_old_backups(directory: Path, keep_count: int | None = None) -> None:
    """
    Remove old backup files, keeping only the most recent ones.

    Args:
        directory: Directory containing backup files
        keep_count: Number of recent backups to keep (defaults to settings)
    """
    if keep_count is None:
        keep_count = settings.DATABASE_BACKUP_KEEP
    try:
        # One retention window across every database format -- keeping N
        # of each would double the footprint the setting is meant to bound.
        # Storage snapshots are a different thing and keep the same N.
        for patterns in (BACKUP_FILE_PATTERNS, STORAGE_BACKUP_PATTERNS):
            backup_files = list_backups(directory, patterns)

            # Remove old backups beyond keep_count
            old_backups = backup_files[keep_count:]
            for old_backup in old_backups:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup.name}")

            if old_backups:
                kept_count = min(len(backup_files), keep_count)
                logger.info(
                    f"Cleaned up {len(old_backups)} old backups, kept {kept_count}"
                )

    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")


def _restore_command(backup_path: Path) -> list[str]:
    """The client invocation that restores ``backup_path``.

    Custom-format dumps need pg_restore; the older plain dumps are SQL text
    and still need psql. ``--clean --if-exists`` makes the restore
    idempotent against a populated database instead of failing on every
    object that already exists.
    """
    if backup_path.suffix == LEGACY_BACKUP_FILE_SUFFIX:
        return ["psql", client_url(), "-f", str(backup_path)]
    return [
        "pg_restore",
        "-d",
        client_url(),
        "--clean",
        "--if-exists",
        str(backup_path),
    ]


async def restore_database_from_backup(backup_filename: str) -> bool:
    """
    Restore database from a backup file.

    Args:
        backup_filename: Name of the backup file to restore from

    Returns:
        True if restore was successful, False otherwise
    """
    try:
        directory = backup_dir()
        backup_path = directory / backup_filename

        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False

        # Create backup before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_path = (
            directory / f"pre_restore_backup_{timestamp}{BACKUP_FILE_SUFFIX}"
        )
        pre_result = await _run_blocking(
            [
                "pg_dump",
                client_url(),
                "-Fc",
                "-f",
                str(pre_restore_path),
            ]
        )
        if pre_result.returncode == 0:
            logger.info(f"Created pre-restore backup: {pre_restore_path}")

        # Restore with the client that matches the dump's format
        result = await _run_blocking(_restore_command(backup_path))
        if result.returncode == 0:
            logger.info(f"Database restored from backup: {backup_filename}")
            return True
        else:
            logger.error(f"restore failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False

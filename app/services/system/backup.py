"""
Database backup service for sector-7g.

Provides database backup functionality for scheduled backup jobs.
Included when scheduler and database components are both present.
"""


import asyncio

import subprocess

from datetime import datetime
from pathlib import Path


from app.core.config import settings

from app.core.log import logger

# Backup file naming pattern

BACKUP_FILE_PATTERN = "database_backup_*.sql"
BACKUP_FILE_PREFIX = "database_backup_"



async def backup_database_job() -> None:
    """
    Scheduled database backup job.


    Creates a backup of the PostgreSQL database using pg_dump.

    Keeps the last 7 daily backups to prevent disk space issues.
    """
    try:
        # Ensure backup directory exists
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_filename = f"{BACKUP_FILE_PREFIX}{timestamp}.sql"
        backup_path = backup_dir / backup_filename

        # Run pg_dump to create backup
        result = subprocess.run(
            ["pg_dump", settings.database_url_effective, "-f", str(backup_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_path}")
        else:
            logger.error(f"pg_dump failed: {result.stderr}")


        # Clean up old backups (keep last 7) - always run regardless of backup success
        await _cleanup_old_backups(backup_dir)

    except Exception as e:
        logger.error(f"Database backup failed: {e}")


async def _cleanup_old_backups(backup_dir: Path, keep_count: int = 7) -> None:
    """
    Remove old backup files, keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backup files
        keep_count: Number of recent backups to keep
    """
    try:
        # Get all backup files sorted by modification time (newest first)
        backup_files = [
            f for f in backup_dir.glob(BACKUP_FILE_PATTERN)
            if f.is_file()
        ]
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

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


async def restore_database_from_backup(backup_filename: str) -> bool:
    """
    Restore database from a backup file.

    Args:
        backup_filename: Name of the backup file to restore from

    Returns:
        True if restore was successful, False otherwise
    """
    try:
        backup_dir = Path("backups")
        backup_path = backup_dir / backup_filename

        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False


        # Create backup before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_path = backup_dir / f"pre_restore_backup_{timestamp}.sql"
        pre_result = subprocess.run(
            ["pg_dump", settings.database_url_effective, "-f", str(pre_restore_path)],
            capture_output=True,
            text=True,
        )
        if pre_result.returncode == 0:
            logger.info(f"Created pre-restore backup: {pre_restore_path}")

        # Restore from backup using psql
        result = subprocess.run(
            ["psql", settings.database_url_effective, "-f", str(backup_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"Database restored from backup: {backup_filename}")
            return True
        else:
            logger.error(f"psql restore failed: {result.stderr}")
            return False


    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False

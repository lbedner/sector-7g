"""
Scheduler component for sector-7g.

Simple, explicit job scheduling - just import functions and schedule them.
Add your own jobs by importing service functions and calling scheduler.add_job().
"""

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.core.db import engine, init_database, db_session
from app.services.scheduler.models import APSchedulerJob
from app.services.system.backup import backup_database_job



from app.core.config import settings
from app.core.log import logger



def _job_exists_in_database(job_id: str) -> bool:
    """Check if a job already exists in the persistence database using SQLModel."""
    try:
        from sqlmodel import select

        with db_session() as session:
            # Query for job by ID using modern SQLModel pattern
            query = select(APSchedulerJob).where(APSchedulerJob.id == job_id)
            result = session.exec(query)
            job = result.first()
            return job is not None
    except Exception as e:
        logger.warning(f"Could not check for existing job {job_id}: {e}")
        # If we can't check, assume it doesn't exist (safer to add than skip)
        return False






def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler with all jobs."""

    # Ensure database is initialized before creating jobstore
    init_database()

    # Configure SQLAlchemy jobstore for persistence
    jobstore = SQLAlchemyJobStore(engine=engine, tablename='apscheduler_jobs')
    jobstores = {'default': jobstore}
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    logger.info("Scheduler using postgres database for job persistence")


    # ============================================================================
    # JOB SCHEDULE CONFIGURATION
    #
    # PERSISTENCE BEHAVIOR:
    # - Jobs are checked against the database first
    # - Existing jobs are preserved (respects runtime modifications)
    # - New jobs are added from code configuration
    # - Set SCHEDULER_FORCE_UPDATE=true to override all jobs from code
    #
    # To update schedules during deployment:
    #   SCHEDULER_FORCE_UPDATE=true docker-compose up -d scheduler
    # ============================================================================


    # Check config flag for force updates (useful during deployments)
    force_update = settings.SCHEDULER_FORCE_UPDATE
    # Database backup job (runs daily at 2 AM when database is available)
    job_id = "database_backup"

    # For persistent schedulers, check database directly since
    # scheduler hasn't loaded jobs yet
    job_exists = _job_exists_in_database(job_id)


    if not job_exists or force_update:
        if job_exists and force_update:
            logger.info(f"Force updating job '{job_id}' from code configuration")
        else:
            logger.info(f"Adding new job '{job_id}'")

        scheduler.add_job(
            backup_database_job,
            trigger="cron",
            hour=2,
            minute=0,
            id=job_id,
            name="Daily Database Backup",
            max_instances=1,
            coalesce=True,
            replace_existing=True  # Safe to use since we check first
        )
    else:

        msg = f"Job '{job_id}' exists in database, preserving current configuration"
        logger.info(msg)





    # Add your own scheduled jobs here by importing service functions
    # and calling scheduler.add_job() with your custom business logic

    return scheduler


async def run_scheduler() -> None:
    """Main scheduler runner with lifecycle management."""

    logger.info("Starting sector-7g Scheduler")

    scheduler = create_scheduler()

    try:
        scheduler.start()
        logger.info("Scheduler started successfully")
        logger.info(f"{len(scheduler.get_jobs())} jobs scheduled:")

        for job in scheduler.get_jobs():
            logger.info(f"   • {job.name} - {job.trigger}")


        # Keep the scheduler running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise
    finally:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped gracefully")

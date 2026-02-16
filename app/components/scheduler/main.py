"""
Scheduler component for sector-7g.

Simple, explicit job scheduling - just import functions and schedule them.
Add your own jobs by importing service functions and calling scheduler.add_job().
"""

import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.db import db_session, engine, init_database
from app.core.log import logger
from app.services.scheduler.models import APSchedulerJob
from app.services.springfield.scheduler_jobs import (
    afternoon_diagnostics,
    burns_announcement,
    burns_opens_plant,
    carl_files_reports,
    cooling_tower_check,
    end_of_shift,
    evening_handoff,
    health_inspector_visit,
    homer_alarm_snooze,
    homer_another_donut,
    homer_clocks_in,
    homer_descends_to_7g,
    homer_nap_attempt,
    homer_safety_check,
    lenny_carl_arrive,
    lunch_at_moes,
    morning_donut_run,
    night_maintenance_job,
    sector_7g_inspection,
    smithers_morning_briefing,
)
from app.services.springfield.simulation import (
    generate_carl_work,
    generate_charlie_work,
    generate_grimey_work,
    generate_homer_work,
    generate_inanimate_rod_work,
    generate_lenny_work,
)
from app.services.system.backup import backup_database_job


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


def _add_cron_job(
    scheduler: AsyncIOScheduler,
    func: object,
    job_id: str,
    name: str,
    hour: int,
    minute: int,
    force_update: bool,
) -> None:
    """Add a cron job with persistence-aware logic."""
    job_exists = _job_exists_in_database(job_id)

    if not job_exists or force_update:
        if job_exists and force_update:
            logger.info(f"Force updating job '{job_id}' from code configuration")
        else:
            logger.info(f"Adding new job '{job_id}'")

        scheduler.add_job(
            func,
            trigger="cron",
            hour=hour,
            minute=minute,
            timezone="America/Chicago",
            id=job_id,
            name=name,
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    else:
        msg = f"Job '{job_id}' exists in database, preserving"
        logger.info(msg)


def _add_interval_job(
    scheduler: AsyncIOScheduler,
    func: object,
    job_id: str,
    name: str,
    seconds: int,
    force_update: bool,
) -> None:
    """Add an interval job with persistence-aware logic."""
    job_exists = _job_exists_in_database(job_id)

    if not job_exists or force_update:
        if job_exists and force_update:
            logger.info(f"Force updating job '{job_id}' from code configuration")
        else:
            logger.info(f"Adding new job '{job_id}'")

        scheduler.add_job(
            func,
            trigger="interval",
            seconds=seconds,
            id=job_id,
            name=name,
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    else:
        msg = f"Job '{job_id}' exists in database, preserving"
        logger.info(msg)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler with all jobs."""

    # Ensure database is initialized before creating jobstore
    init_database()

    # Configure SQLAlchemy jobstore for persistence
    jobstore = SQLAlchemyJobStore(engine=engine, tablename="apscheduler_jobs")
    jobstores = {"default": jobstore}
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

    # Database backup job (runs daily at 2 AM)
    job_id = "database_backup"
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
            replace_existing=True,
        )
    else:
        msg = f"Job '{job_id}' exists in database, preserving"
        logger.info(msg)

    # ============================================================================
    # SPRINGFIELD NUCLEAR POWER PLANT — DAILY TIMELINE
    # All times in America/Chicago (Springfield local time)
    # ============================================================================

    # fmt: off
    springfield_jobs = [
        (burns_opens_plant,         "burns_opens_plant",         "Burns Opens Plant",          6,  0),  # noqa: E501
        (smithers_morning_briefing, "smithers_morning_briefing", "Smithers Morning Briefing",  6, 30),  # noqa: E501
        (lenny_carl_arrive,         "lenny_carl_arrive",         "Lenny & Carl Arrive",        7,  0),  # noqa: E501
        (homer_alarm_snooze,        "homer_alarm_snooze",        "Homer Alarm Snooze",         7, 45),  # noqa: E501
        (homer_clocks_in,           "homer_clocks_in",           "Homer Clocks In (Late)",     8, 15),  # noqa: E501
        (morning_donut_run,         "morning_donut_run",         "Morning Donut Run",          8, 30),  # noqa: E501
        (sector_7g_inspection,      "sector_7g_inspection",      "Sector 7G Inspection",       9,  0),  # noqa: E501
        (homer_descends_to_7g,      "homer_descends_to_7g",      "Homer Descends to 7G",       9, 45),  # noqa: E501
        (health_inspector_visit,    "health_inspector_visit",    "NRC Inspector Visit",       10,  0),  # noqa: E501
        (homer_nap_attempt,         "homer_nap_attempt",         "Homer Nap Attempt",         10, 30),  # noqa: E501
        (burns_announcement,        "burns_announcement",        "Burns Announcement",        11, 30),  # noqa: E501
        (lunch_at_moes,             "lunch_at_moes",             "Lunch at Moe's",            12,  0),  # noqa: E501
        (afternoon_diagnostics,     "afternoon_diagnostics",     "Afternoon Diagnostics",     13,  0),  # noqa: E501
        (homer_safety_check,        "homer_safety_check",        "Homer Safety Check",        14,  0),  # noqa: E501
        (carl_files_reports,        "carl_files_reports",        "Carl Files Reports",        15,  0),  # noqa: E501
        (cooling_tower_check,       "cooling_tower_check",       "Cooling Tower Check",       16,  0),  # noqa: E501
        (homer_another_donut,       "homer_another_donut",       "Homer Afternoon Donut",     16, 30),  # noqa: E501
        (end_of_shift,              "end_of_shift",              "End of Shift",              17,  0),  # noqa: E501
        (evening_handoff,           "evening_handoff",           "Evening Shift Handoff",     17, 30),  # noqa: E501
        (night_maintenance_job,     "night_maintenance",         "Night Maintenance",         22,  0),  # noqa: E501
    ]
    # fmt: on

    for func, job_id, name, hour, minute in springfield_jobs:
        _add_cron_job(scheduler, func, job_id, name, hour, minute, force_update)

    # ============================================================================
    # CONTINUOUS SIMULATION — interval jobs that keep queues busy
    # Homer gets more work than he can handle (backlog builds).
    # Everyone else clears instantly.
    # ============================================================================

    # fmt: off
    simulation_jobs = [
        (generate_homer_work,  "sim_homer",  "Homer Simulation Work",  10),    # noqa: E501
        (generate_lenny_work,  "sim_lenny",  "Lenny Simulation Work",  15),    # noqa: E501
        (generate_carl_work,    "sim_carl",    "Carl Simulation Work",    15),   # noqa: E501
        (generate_charlie_work, "sim_charlie", "Charlie Simulation Work", 15),  # noqa: E501
        (generate_inanimate_rod_work, "sim_inanimate_rod", "Inanimate Rod Simulation Work", 45),  # noqa: E501
        (generate_grimey_work, "sim_grimey", "Grimey Simulation Work", 3600),  # noqa: E501
    ]
    # fmt: on

    for func, job_id, name, seconds in simulation_jobs:
        _add_interval_job(scheduler, func, job_id, name, seconds, force_update)

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

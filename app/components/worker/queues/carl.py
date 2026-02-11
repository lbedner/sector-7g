"""
Carl Carlson worker queue configuration.

High concurrency + fast I/O = tasks clear quickly. Same as Lenny.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.carl_tasks import (
    file_afternoon_reports_task,
    handle_inspector_task,
    make_announcement_task,
    morning_briefing_task,
    shift_handoff_task,
)
from app.components.worker.tasks.simulation_tasks import carl_sim_task
from app.core.config import settings


class WorkerSettings:
    """Carl's worker — efficient and reliable."""

    description = "Carl Carlson, Technical Supervisor"

    functions = [
        handle_inspector_task,
        file_afternoon_reports_task,
        shift_handoff_task,
        make_announcement_task,
        morning_briefing_task,
        carl_sim_task,
    ]

    base_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    redis_settings = RedisSettings(
        host=base_settings.host,
        port=base_settings.port,
        database=base_settings.database,
        password=base_settings.password,
        conn_timeout=settings.REDIS_CONN_TIMEOUT,
        conn_retries=settings.REDIS_CONN_RETRIES,
        conn_retry_delay=settings.REDIS_CONN_RETRY_DELAY,
    )
    queue_name = "arq:queue:carl"
    max_jobs = 15
    job_timeout = 120
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    max_tries = settings.WORKER_MAX_TRIES
    health_check_interval = settings.WORKER_HEALTH_CHECK_INTERVAL

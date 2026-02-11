"""
Lenny Leonard worker queue configuration.

High concurrency + fast I/O = tasks clear quickly. Competent worker.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.lenny_tasks import (
    check_cooling_tower_task,
    file_report_task,
    morning_inspection_task,
    night_maintenance_task,
    open_plant_task,
    run_diagnostics_task,
)
from app.components.worker.tasks.simulation_tasks import lenny_sim_task
from app.core.config import settings


class WorkerSettings:
    """Lenny's worker — competent and efficient."""

    description = "Lenny Leonard, Technical Supervisor"

    functions = [
        run_diagnostics_task,
        file_report_task,
        check_cooling_tower_task,
        morning_inspection_task,
        open_plant_task,
        night_maintenance_task,
        lenny_sim_task,
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
    queue_name = "arq:queue:lenny"
    max_jobs = 15
    job_timeout = 120
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    max_tries = settings.WORKER_MAX_TRIES
    health_check_interval = settings.WORKER_HEALTH_CHECK_INTERVAL

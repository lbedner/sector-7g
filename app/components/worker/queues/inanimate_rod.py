"""
Inanimate Carbon Rod worker queue configuration.

Employee of the Month. Handles system maintenance + Rod simulation tasks.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.inanimate_rod_tasks import inanimate_rod_sim_task
from app.components.worker.tasks.simple_system_tasks import (
    cleanup_temp_files,
    system_health_check,
)
from app.core.config import settings


class WorkerSettings:
    """Inanimate Carbon Rod — Employee of the Month."""

    description = "Inanimate Carbon Rod, Employee of the Month"

    functions = [
        system_health_check,
        cleanup_temp_files,
        inanimate_rod_sim_task,
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
    queue_name = "arq:queue:inanimate_rod"
    max_jobs = 15
    job_timeout = 300
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    max_tries = settings.WORKER_MAX_TRIES
    health_check_interval = settings.WORKER_HEALTH_CHECK_INTERVAL

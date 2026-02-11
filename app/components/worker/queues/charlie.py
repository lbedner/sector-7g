"""
Charlie worker queue configuration.

Moderate concurrency, steady I/O-bound tasks. Just a regular plant worker.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.charlie_tasks import (
    check_emergency_exits_task,
    log_shift_notes_task,
    monitor_gauges_task,
    restock_break_room_task,
)
from app.components.worker.tasks.simulation_tasks import charlie_sim_task
from app.core.config import settings


class WorkerSettings:
    """Charlie — Plant Worker."""

    description = "Charlie, Plant Worker"

    functions = [
        monitor_gauges_task,
        restock_break_room_task,
        log_shift_notes_task,
        check_emergency_exits_task,
        charlie_sim_task,
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
    queue_name = "arq:queue:charlie"
    max_jobs = 10
    job_timeout = 120
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    max_tries = settings.WORKER_MAX_TRIES
    health_check_interval = settings.WORKER_HEALTH_CHECK_INTERVAL

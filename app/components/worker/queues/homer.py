"""
Homer Simpson worker queue configuration.

Low concurrency + CPU-bound tasks = visible backlog. That's the joke.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.homer_tasks import (
    attempt_safety_check_task,
    clock_in_task,
    eat_donut_task,
    go_to_moes_task,
    nap_at_console_task,
    rush_out_task,
)
from app.components.worker.tasks.simulation_tasks import homer_sim_task
from app.core.config import settings


class WorkerSettings:
    """Homer's worker — barely handles one thing at a time."""

    description = "Homer Simpson, Safety Inspector Sector 7G"

    functions = [
        eat_donut_task,
        nap_at_console_task,
        attempt_safety_check_task,
        clock_in_task,
        go_to_moes_task,
        rush_out_task,
        homer_sim_task,
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
    queue_name = "arq:queue:homer"
    max_jobs = 3
    job_timeout = 600
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    # Homer's "D'oh!" failures are intentional character behavior —
    # retrying them just clogs an already-saturated queue
    max_tries = 1
    # Homer is perpetually saturated — long TTL so the heartbeat key survives
    # between the rare moments arq gets to write it
    health_check_interval = 120

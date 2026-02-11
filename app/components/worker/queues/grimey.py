"""
Frank Grimes (deceased) worker queue configuration.

One ghost, one task at a time. Meticulous, thorough, zero failures.
"""

from arq.connections import RedisSettings

from app.components.worker.tasks.grimey_tasks import grimey_sim_task
from app.core.config import settings


class WorkerSettings:
    """Frank Grimes (deceased) — Employee #4763."""

    description = "Frank Grimes (deceased), Employee #4763"

    functions = [
        grimey_sim_task,
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
    queue_name = "arq:queue:grimey"
    max_jobs = 1  # One ghost, one task at a time
    job_timeout = 600
    keep_result = settings.WORKER_KEEP_RESULT_SECONDS
    # Grimey doesn't fail (0% rate), but set to 1 for consistency
    max_tries = 1
    # Grimey is meticulous — tasks take 10-20s with max_jobs=1, so the arq
    # semaphore blocks heart_beat() for the entire duration.  Long TTL keeps
    # the health-check key alive between tasks.
    health_check_interval = 60

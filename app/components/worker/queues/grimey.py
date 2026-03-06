"""
Frank Grimes (deceased) worker queue configuration.

One ghost, one task at a time. Meticulous, thorough, zero failures.
"""

from typing import Any

from arq.connections import RedisSettings
from arq.constants import result_key_prefix
from arq.jobs import deserialize_result
import redis.asyncio as aioredis

from app.components.worker.events import publish_event
from app.components.worker.tasks.grimey_tasks import grimey_sim_task
from app.core.config import settings
from app.core.log import logger


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

    @staticmethod
    async def on_startup(ctx: dict[str, Any]) -> None:
        """Publish worker.started event on worker startup."""
        try:
            redis_url = (
                settings.redis_url_effective
                if hasattr(settings, "redis_url_effective")
                else settings.REDIS_URL
            )
            ctx["events_redis"] = aioredis.from_url(redis_url)
            ctx["worker_queue_name"] = "grimey"
            await publish_event(ctx["events_redis"], "worker.started", "grimey")
        except Exception as e:
            logger.debug(f"Failed to initialize event publishing: {e}")

    @staticmethod
    async def on_shutdown(ctx: dict[str, Any]) -> None:
        """Publish worker.stopped event on worker shutdown."""
        if "events_redis" in ctx:
            await publish_event(ctx["events_redis"], "worker.stopped", "grimey")
            await ctx["events_redis"].aclose()

    @staticmethod
    async def on_job_start(ctx: dict[str, Any]) -> None:
        """Publish job.started event when a job begins processing."""
        if "events_redis" in ctx:
            await publish_event(
                ctx["events_redis"],
                "job.started",
                ctx.get("worker_queue_name", "grimey"),
                {"job_id": str(ctx.get("job_id", "unknown"))},
            )

    @staticmethod
    async def after_job_end(ctx: dict[str, Any]) -> None:
        """Publish job.completed or job.failed event after each job."""
        if "events_redis" not in ctx:
            return
        job_id = str(ctx.get("job_id", "unknown"))
        queue = ctx.get("worker_queue_name", "grimey")
        success = True
        try:
            raw = await ctx["events_redis"].get(result_key_prefix + job_id)
            if raw:
                result = deserialize_result(raw)
                success = result.success
        except Exception:
            pass
        event_type = "job.completed" if success else "job.failed"
        await publish_event(
            ctx["events_redis"], event_type, queue,
            {"job_id": job_id, "status": "success" if success else "failed"},
        )

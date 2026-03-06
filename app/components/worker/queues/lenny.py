"""
Lenny Leonard worker queue configuration.

High concurrency + fast I/O = tasks clear quickly. Competent worker.
"""

from typing import Any

from arq.connections import RedisSettings
from arq.constants import result_key_prefix
from arq.jobs import deserialize_result
import redis.asyncio as aioredis

from app.components.worker.events import publish_event
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
from app.core.log import logger


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
            ctx["worker_queue_name"] = "lenny"
            await publish_event(ctx["events_redis"], "worker.started", "lenny")
        except Exception as e:
            logger.debug(f"Failed to initialize event publishing: {e}")

    @staticmethod
    async def on_shutdown(ctx: dict[str, Any]) -> None:
        """Publish worker.stopped event on worker shutdown."""
        if "events_redis" in ctx:
            await publish_event(ctx["events_redis"], "worker.stopped", "lenny")
            await ctx["events_redis"].aclose()

    @staticmethod
    async def on_job_start(ctx: dict[str, Any]) -> None:
        """Publish job.started event when a job begins processing."""
        if "events_redis" in ctx:
            await publish_event(
                ctx["events_redis"],
                "job.started",
                ctx.get("worker_queue_name", "lenny"),
                {"job_id": str(ctx.get("job_id", "unknown"))},
            )

    @staticmethod
    async def after_job_end(ctx: dict[str, Any]) -> None:
        """Publish job.completed or job.failed event after each job."""
        if "events_redis" not in ctx:
            return
        job_id = str(ctx.get("job_id", "unknown"))
        queue = ctx.get("worker_queue_name", "lenny")
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

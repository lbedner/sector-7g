"""
Homer Simpson worker queue configuration.

Low concurrency + CPU-bound tasks = visible backlog. That's the joke.
"""

from typing import Any

from arq.connections import RedisSettings
from arq.constants import result_key_prefix
from arq.jobs import deserialize_result
import redis.asyncio as aioredis

from app.components.worker.events import publish_event
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
from app.core.log import logger


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
            ctx["worker_queue_name"] = "homer"
            await publish_event(ctx["events_redis"], "worker.started", "homer")
        except Exception as e:
            logger.debug(f"Failed to initialize event publishing: {e}")

    @staticmethod
    async def on_shutdown(ctx: dict[str, Any]) -> None:
        """Publish worker.stopped event on worker shutdown."""
        if "events_redis" in ctx:
            await publish_event(ctx["events_redis"], "worker.stopped", "homer")
            await ctx["events_redis"].aclose()

    @staticmethod
    async def on_job_start(ctx: dict[str, Any]) -> None:
        """Publish job.started event and record task history."""
        if "events_redis" not in ctx:
            return
        job_id = str(ctx.get("job_id", "unknown"))
        await publish_event(
            ctx["events_redis"],
            "job.started",
            ctx.get("worker_queue_name", "homer"),
            {"job_id": job_id},
        )
        # Record task started in history
        from app.components.worker.task_history import (
            record_task_started,
            resolve_arq_task_name,
        )

        task_name = await resolve_arq_task_name(ctx["events_redis"], job_id)
        await record_task_started(
            ctx["events_redis"],
            job_id,
            task_name=task_name,
            queue_name="homer",
        )

    @staticmethod
    async def after_job_end(ctx: dict[str, Any]) -> None:
        """Publish job result event and record task history."""
        if "events_redis" not in ctx:
            return
        job_id = str(ctx.get("job_id", "unknown"))
        queue = ctx.get("worker_queue_name", "homer")
        success = True
        error_msg: str | None = None
        task_name: str | None = None
        try:
            raw = await ctx["events_redis"].get(result_key_prefix + job_id)
            if raw:
                result = deserialize_result(raw)
                success = result.success
                task_name = getattr(result, "function", None)
                if not success:
                    error_msg = str(getattr(result, "result", ""))[:2000]
        except Exception:
            pass
        event_type = "job.completed" if success else "job.failed"
        await publish_event(
            ctx["events_redis"], event_type, queue,
            {"job_id": job_id, "status": "success" if success else "failed"},
        )
        # Record task finished in history
        from app.components.worker.task_history import record_task_finished

        await record_task_finished(
            ctx["events_redis"],
            job_id,
            success=success,
            error=error_msg,
            task_name=task_name,
            queue_name=queue,
        )

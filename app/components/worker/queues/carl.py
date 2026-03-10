"""
Carl Carlson worker queue configuration.

High concurrency + fast I/O = tasks clear quickly. Same as Lenny.
"""

from typing import Any

from arq.connections import RedisSettings
from arq.constants import result_key_prefix
from arq.jobs import deserialize_result
import redis.asyncio as aioredis

from app.components.worker.events import publish_event
from app.components.worker.tasks.carl_tasks import (
    file_afternoon_reports_task,
    handle_inspector_task,
    make_announcement_task,
    morning_briefing_task,
    shift_handoff_task,
)
from app.components.worker.tasks.simulation_tasks import carl_sim_task
from app.core.config import settings
from app.core.log import logger


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
            ctx["worker_queue_name"] = "carl"
            await publish_event(ctx["events_redis"], "worker.started", "carl")
        except Exception as e:
            logger.debug(f"Failed to initialize event publishing: {e}")

    @staticmethod
    async def on_shutdown(ctx: dict[str, Any]) -> None:
        """Publish worker.stopped event on worker shutdown."""
        if "events_redis" in ctx:
            await publish_event(ctx["events_redis"], "worker.stopped", "carl")
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
            ctx.get("worker_queue_name", "carl"),
            {"job_id": job_id},
        )
        from app.components.worker.task_history import (
            record_task_started,
            resolve_arq_task_name,
        )

        task_name = await resolve_arq_task_name(ctx["events_redis"], job_id)
        await record_task_started(
            ctx["events_redis"],
            job_id,
            task_name=task_name,
            queue_name="carl",
        )

    @staticmethod
    async def after_job_end(ctx: dict[str, Any]) -> None:
        """Publish job result event and record task history."""
        if "events_redis" not in ctx:
            return
        job_id = str(ctx.get("job_id", "unknown"))
        queue = ctx.get("worker_queue_name", "carl")
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
        from app.components.worker.task_history import record_task_finished

        await record_task_finished(
            ctx["events_redis"],
            job_id,
            success=success,
            error=error_msg,
            task_name=task_name,
            queue_name=queue,
        )

"""Scheduled service jobs, run as worker tasks on the system queue.

The scheduler enqueues each job by its function's name; this is where the
worker learns those names. Both read ``app.core.schedule.service_jobs``,
so the two cannot drift apart.
"""

import functools
from typing import Any

from app.core.schedule import ServiceJob, service_jobs


def as_task(job: ServiceJob, broker: Any) -> Any:
    """One job as a TaskIQ task under the job's own name and timeout.

    TaskIQ renames the function it decorates (``__name__`` gains
    ``__taskiq_original``), so it decorates a wrapper of our own: the job's
    function is shared with the scheduler, which enqueues by its name.
    """

    @functools.wraps(job.func)  # the job's own code: what it goes into
    async def run() -> Any:
        return await job.run()

    run.__name__ = run.__qualname__ = job.task_name
    run.__doc__ = job.func.__doc__
    labels = {"timeout": job.timeout} if job.timeout else {}
    return broker.task(task_name=job.task_name, **labels)(run)


def service_job_tasks(broker: Any) -> dict[str, Any]:
    """Every scheduled job, keyed by name, registered on ``broker``.

    The registry reads a queue's tasks off its module, so the queue binds
    these as module attributes.
    """
    return {job.task_name: as_task(job, broker) for job in service_jobs()}

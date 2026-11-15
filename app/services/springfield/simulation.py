"""
Springfield Nuclear Power Plant — Continuous Job Simulation.

Generates batches of simulation tasks at regular intervals to keep
all queues busy. Homer's queue intentionally builds a backlog while
competent workers clear instantly.
"""

import random

from redis.exceptions import ResponseError

from app.components.worker import pools
from app.components.worker.events import events_redis
from app.core.constants import QueueName
from app.core.log import logger
from app.services.system.health_worker_rules import taskiq_group_stats


async def waiting_jobs(queue: str) -> int:
    """Jobs on ``queue`` no worker has finished: not yet read (what the
    Overseer calls queued), plus read and still held."""
    stream = pools.get_broker(queue).queue_name
    pipe = (await events_redis()).pipeline(transaction=False)
    pipe.xlen(stream)
    pipe.xinfo_groups(stream)
    length, groups = await pipe.execute(raise_on_error=False)
    if isinstance(groups, ResponseError):  # no stream yet: nothing was sent
        return 0
    _, pending, _, lag = taskiq_group_stats(groups, length)
    return lag + pending


async def _generate(queue: str, task: str, low: int, high: int, cap: int) -> None:
    """Enqueue ``low``-``high`` of ``task`` on ``queue``, unless more than
    ``cap`` are already waiting."""
    depth = await waiting_jobs(queue)
    if depth > cap:
        logger.debug(f"{queue} queue at {depth}, skipping batch (cap: {cap})")
        return

    count = random.randint(low, high)
    for _ in range(count):
        await pools.enqueue_task(task, queue)
    logger.info(f"Simulation: enqueued {count} {queue} tasks (depth: {depth})")


# One named function per character: the scheduler keeps each job by the
# function it calls.
async def generate_homer_work() -> None:
    """3-5 Homer tasks. Cap at 500 waiting."""
    await _generate(QueueName.HOMER, "homer_sim_task", 3, 5, 500)


async def generate_lenny_work() -> None:
    """4-6 Lenny tasks. Cap at 100 waiting."""
    await _generate(QueueName.LENNY, "lenny_sim_task", 4, 6, 100)


async def generate_carl_work() -> None:
    """4-6 Carl tasks. Cap at 100 waiting."""
    await _generate(QueueName.CARL, "carl_sim_task", 4, 6, 100)


async def generate_inanimate_rod_work() -> None:
    """2-3 Inanimate Rod tasks. Cap at 50 waiting."""
    await _generate(QueueName.INANIMATE_ROD, "inanimate_rod_sim_task", 2, 3, 50)


async def generate_charlie_work() -> None:
    """4-6 Charlie tasks. Cap at 100 waiting."""
    await _generate(QueueName.CHARLIE, "charlie_sim_task", 4, 6, 100)


async def generate_grimey_work() -> None:
    """1 Grimey task. Cap at 5 waiting."""
    await _generate(QueueName.GRIMEY, "grimey_sim_task", 1, 1, 5)

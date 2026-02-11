"""
Springfield Nuclear Power Plant — Continuous Job Simulation.

Generates batches of simulation tasks at regular intervals to keep
all queues busy. Homer's queue intentionally builds a backlog while
competent workers clear instantly.
"""

import random

from app.core.log import logger


async def _get_queue_depth(pool, queue_name: str) -> int:  # noqa: ANN001
    """Get approximate queue depth from Redis."""
    try:
        return await pool.zcard(queue_name)
    except Exception:
        return 0


async def generate_homer_work() -> None:
    """Enqueue 3-5 Homer simulation tasks. Cap at 500 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("homer")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 500:
            logger.debug(f"Homer queue at {depth}, skipping batch (cap: 500)")
            return

        count = random.randint(3, 5)
        for _ in range(count):
            await pool.enqueue_job("homer_sim_task", _queue_name=queue_name)
        logger.info(f"Simulation: enqueued {count} Homer tasks (depth: {depth})")
    finally:
        await pool.aclose()


async def generate_lenny_work() -> None:
    """Enqueue 4-6 Lenny simulation tasks. Cap at 100 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("lenny")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 100:
            logger.debug(f"Lenny queue at {depth}, skipping batch (cap: 100)")
            return

        count = random.randint(4, 6)
        for _ in range(count):
            await pool.enqueue_job("lenny_sim_task", _queue_name=queue_name)
        logger.info(f"Simulation: enqueued {count} Lenny tasks (depth: {depth})")
    finally:
        await pool.aclose()


async def generate_carl_work() -> None:
    """Enqueue 4-6 Carl simulation tasks. Cap at 100 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("carl")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 100:
            logger.debug(f"Carl queue at {depth}, skipping batch (cap: 100)")
            return

        count = random.randint(4, 6)
        for _ in range(count):
            await pool.enqueue_job("carl_sim_task", _queue_name=queue_name)
        logger.info(f"Simulation: enqueued {count} Carl tasks (depth: {depth})")
    finally:
        await pool.aclose()


async def generate_inanimate_rod_work() -> None:
    """Enqueue 2-3 Inanimate Rod simulation tasks. Cap at 50 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("inanimate_rod")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 50:
            logger.debug(f"Inanimate Rod queue at {depth}, skipping batch (cap: 50)")
            return

        count = random.randint(2, 3)
        for _ in range(count):
            await pool.enqueue_job(
                "inanimate_rod_sim_task", _queue_name=queue_name
            )
        logger.info(
            f"Simulation: enqueued {count} Inanimate Rod tasks (depth: {depth})"
        )
    finally:
        await pool.aclose()


async def generate_charlie_work() -> None:
    """Enqueue 4-6 Charlie simulation tasks. Cap at 100 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("charlie")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 100:
            logger.debug(f"Charlie queue at {depth}, skipping batch (cap: 100)")
            return

        count = random.randint(4, 6)
        for _ in range(count):
            await pool.enqueue_job("charlie_sim_task", _queue_name=queue_name)
        logger.info(f"Simulation: enqueued {count} Charlie tasks (depth: {depth})")
    finally:
        await pool.aclose()


async def generate_grimey_work() -> None:
    """Enqueue 1 Grimey simulation task. Cap at 5 queued."""
    from app.components.worker.pools import get_queue_pool

    pool, queue_name = await get_queue_pool("grimey")
    try:
        depth = await _get_queue_depth(pool, queue_name)
        if depth > 5:
            logger.debug(f"Grimey queue at {depth}, skipping batch (cap: 5)")
            return

        await pool.enqueue_job("grimey_sim_task", _queue_name=queue_name)
        logger.info(f"Simulation: enqueued 1 Grimey task (depth: {depth})")
    finally:
        await pool.aclose()

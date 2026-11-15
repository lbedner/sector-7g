"""The plant's six queues: built one way, and everything Springfield
enqueues has a worker that runs it."""

from typing import Any

import pytest

from app.components.worker import pools
from app.components.worker.registry import discover_worker_queues, queue_tasks
from app.core.constants import QueueName
from app.services.springfield import schedules, simulation


def test_the_plant_has_exactly_its_six_queues() -> None:
    assert discover_worker_queues() == sorted(QueueName)


@pytest.mark.asyncio
async def test_everything_springfield_enqueues_is_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A name no worker registers is enqueued and never runs, and it would
    only show at 6 AM when the job fires."""
    sent: list[tuple[str, str]] = []

    async def record(task: str, queue: str, *_a: Any, **_k: Any) -> None:
        sent.append((task, queue))

    async def nothing_waiting(_queue: str) -> int:
        return 0

    monkeypatch.setattr(pools, "enqueue_task", record)
    monkeypatch.setattr(simulation, "waiting_jobs", nothing_waiting)

    jobs = [row[2] for row in schedules._DAILY_ROUTINE + schedules._SIMULATIONS]
    for job in jobs:
        await job()

    assert len(sent) >= len(jobs)
    missing = [(t, q) for t, q in sent if t not in queue_tasks(q)]
    assert not missing

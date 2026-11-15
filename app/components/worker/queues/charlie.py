"""
Charlie's queue.

Moderate concurrency, steady I/O-bound tasks. Just a regular plant worker.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.charlie_tasks import (
    check_emergency_exits_task,
    log_shift_notes_task,
    monitor_gauges_task,
    restock_break_room_task,
)
from app.components.worker.tasks.simulation_tasks import charlie_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Charlie, Plant Worker"

broker = stream_broker(QueueName.CHARLIE)

globals().update(
    bind(
        broker,
        check_emergency_exits_task,
        log_shift_notes_task,
        monitor_gauges_task,
        restock_break_room_task,
        charlie_sim_task,
    )
)

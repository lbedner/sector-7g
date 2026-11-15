"""
Carl Carlson's queue.

High concurrency + fast I/O = tasks clear quickly. Same as Lenny.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.carl_tasks import (
    file_afternoon_reports_task,
    handle_inspector_task,
    make_announcement_task,
    morning_briefing_task,
    shift_handoff_task,
)
from app.components.worker.tasks.simulation_tasks import carl_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Carl Carlson, Technical Supervisor"

broker = stream_broker(QueueName.CARL)

globals().update(
    bind(
        broker,
        file_afternoon_reports_task,
        handle_inspector_task,
        make_announcement_task,
        morning_briefing_task,
        shift_handoff_task,
        carl_sim_task,
    )
)

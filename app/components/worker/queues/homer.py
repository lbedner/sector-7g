"""
Homer Simpson's queue.

Low concurrency + slow tasks = visible backlog. That's the joke.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.homer_tasks import (
    attempt_safety_check_task,
    clock_in_task,
    eat_donut_task,
    go_to_moes_task,
    nap_at_console_task,
    rush_out_task,
)
from app.components.worker.tasks.simulation_tasks import homer_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Homer Simpson, Safety Inspector Sector 7G"

broker = stream_broker(QueueName.HOMER)

globals().update(
    bind(
        broker,
        attempt_safety_check_task,
        clock_in_task,
        eat_donut_task,
        go_to_moes_task,
        nap_at_console_task,
        rush_out_task,
        homer_sim_task,
    )
)

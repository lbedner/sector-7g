"""
The Inanimate Carbon Rod's queue.

Employee of the Month. Runs the Rod simulation and nothing else.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.simulation_tasks import inanimate_rod_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Inanimate Carbon Rod, Employee of the Month"

broker = stream_broker(QueueName.INANIMATE_ROD)

globals().update(
    bind(
        broker,
        inanimate_rod_sim_task,
    )
)

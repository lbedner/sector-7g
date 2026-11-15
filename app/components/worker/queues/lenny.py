"""
Lenny Leonard's queue.

High concurrency + fast I/O = tasks clear quickly. Competent worker.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.lenny_tasks import (
    check_cooling_tower_task,
    file_report_task,
    morning_inspection_task,
    night_maintenance_task,
    open_plant_task,
    run_diagnostics_task,
)
from app.components.worker.tasks.simulation_tasks import lenny_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Lenny Leonard, Technical Supervisor"

broker = stream_broker(QueueName.LENNY)

globals().update(
    bind(
        broker,
        check_cooling_tower_task,
        file_report_task,
        morning_inspection_task,
        night_maintenance_task,
        open_plant_task,
        run_diagnostics_task,
        lenny_sim_task,
    )
)

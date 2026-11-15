"""
Frank Grimes's (deceased) queue.

One ghost, one task at a time. Meticulous, thorough, zero failures.

He also does the stack's own work, the job a ``system`` queue does
elsewhere: scheduled service jobs (the nightly backups), health checks and
cleanup. Nobody at the plant has noticed.
"""

from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.service_jobs import service_job_tasks
from app.components.worker.tasks.simple_system_tasks import (
    cleanup_temp_files,
    system_health_check,
)
from app.components.worker.tasks.simulation_tasks import grimey_sim_task
from app.core.constants import QueueName

DESCRIPTION = "Frank Grimes (deceased), Employee #4763"

broker = stream_broker(QueueName.GRIMEY)

globals().update(
    bind(
        broker,
        grimey_sim_task,
        cleanup_temp_files,
        system_health_check,
    )
)
# The scheduled service jobs (backups among them); the scheduler enqueues
# them by these names.
globals().update(service_job_tasks(broker))

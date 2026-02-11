"""
Dashboard Modal Components

Reusable modal dialogs for displaying detailed component information.
Each modal inherits from ft.AlertDialog and uses component composition.
"""
from .auth_modal import AuthDetailDialog
from .backend_modal import BackendDetailDialog
from .database_modal import DatabaseDetailDialog
from .frontend_modal import FrontendDetailDialog
from .ingress_modal import IngressDetailDialog
from .redis_modal import RedisDetailDialog
from .scheduler_modal import SchedulerDetailDialog
from .worker_modal import WorkerDetailDialog

__all__ = [
    "AuthDetailDialog",
    "BackendDetailDialog",
    "DatabaseDetailDialog",
    "FrontendDetailDialog",
    "IngressDetailDialog",
    "RedisDetailDialog",
    "SchedulerDetailDialog",
    "WorkerDetailDialog",
]
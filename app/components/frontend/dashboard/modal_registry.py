"""The modal registry: which detail dialog a component id opens.

One key per component, shared by the health tree, the card (its
``component_name``), and the status-overview row. A card whose key is
missing here is a dead click, and ``tests/components/frontend/
test_card_modal_keys.py`` walks every card to make sure none is.
"""

import flet as ft

from app.core.constants import ComponentName


def modal_registry() -> dict[str, type[ft.Container]]:
    """Every detail modal, keyed by the component id its card passes.

    Imports live inside so nothing imports the modals package at load.
    """
    # Service modal imports (in-tree + plugins) — absolute paths so
    # external plugins use the same shape as in-tree services.
    # Component / always-present modal imports.
    from app.components.frontend.dashboard.modals.backend_modal import (
        BackendDetailDialog,
    )
    from app.components.frontend.dashboard.modals.database_modal import (
        DatabaseDetailDialog,
    )
    from app.components.frontend.dashboard.modals.frontend_modal import (
        FrontendDetailDialog,
    )
    from app.components.frontend.dashboard.modals.ingress_modal import (
        IngressDetailDialog,
    )
    from app.components.frontend.dashboard.modals.observability_modal import (
        ObservabilityDetailDialog,
    )
    from app.components.frontend.dashboard.modals.redis_modal import RedisDetailDialog
    from app.components.frontend.dashboard.modals.scheduler_modal import (
        SchedulerDetailDialog,
    )
    from app.components.frontend.dashboard.modals.worker_modal import WorkerDetailDialog

    modal_map: dict[str, type[ft.Container]] = {
        ComponentName.BACKEND: BackendDetailDialog,
        ComponentName.FRONTEND: FrontendDetailDialog,
        ComponentName.DATABASE: DatabaseDetailDialog,
        ComponentName.INGRESS: IngressDetailDialog,
        ComponentName.OBSERVABILITY: ObservabilityDetailDialog,
        ComponentName.CACHE: RedisDetailDialog,
        ComponentName.SCHEDULER: SchedulerDetailDialog,
        ComponentName.WORKER: WorkerDetailDialog,
    }

    return modal_map

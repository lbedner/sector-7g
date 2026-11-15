"""Full-page routes for the web frontend.

One handler per page: build the context, hand it to a template. Anything a
page swaps in without a reload belongs in ``routes/partials/`` instead.
"""

from fastapi import APIRouter, Depends

from app.components.web_frontend.overseer_access import overseer_gate
from app.components.web_frontend.routes import overseer as overseer_routes
from app.components.web_frontend.routes.partials import (
    overseer_code as overseer_code_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_database as overseer_database_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_deployments as overseer_deployments_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_errors as overseer_errors_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_redis as overseer_redis_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_runs as overseer_runs_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_runtime as overseer_runtime_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_scheduler as overseer_scheduler_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_secrets as overseer_secrets_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_server as overseer_server_partials,
)
from app.components.web_frontend.routes.partials import (
    overseer_storage as overseer_storage_partials,
)
from app.core.overseer_pages import include_partials

# Every Overseer page, stream and action passes one gate (overseer_access).
router = APIRouter(dependencies=[Depends(overseer_gate)])


# Overseer pages' dialogs and forms (htmx fragments), then its pages: a
# partial's path wins over the pages' catch-all routes.
router.include_router(overseer_scheduler_partials.router)
router.include_router(overseer_secrets_partials.router)
router.include_router(overseer_redis_partials.router)
router.include_router(overseer_storage_partials.router)
router.include_router(overseer_server_partials.router)
router.include_router(overseer_server_partials.load_tests_router)
router.include_router(overseer_server_partials.requests_router)
router.include_router(overseer_runtime_partials.router)
router.include_router(overseer_runs_partials.router)
router.include_router(overseer_database_partials.router)
router.include_router(overseer_deployments_partials.router)
router.include_router(overseer_errors_partials.router)
router.include_router(overseer_code_partials.router)
include_partials(router)
router.include_router(overseer_routes.router)

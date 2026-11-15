"""
Component health registration startup hook.

Automatically detects available components and registers their health checks
with the system health service using Python's import system.

The checks themselves live next door: the backend's own in
``health_backend``, the rest in ``health_components``, and the cached
introspection they read in ``health_metadata``. This module is the
registry - which name maps to which check, gated by what the project
actually ships.
"""

from app.core.constants import ComponentName
from app.core.log import logger
from app.services.system.health import register_health_check

from .health_backend import backend_component_health
from .health_components import scheduler_component_health, web_frontend_component_health
from .health_metadata import (
    initialize_lifecycle_metadata_cache,
    initialize_route_metadata_cache,
)


async def startup_hook() -> None:
    """
    Auto-detect available components and register their health checks.

    Always registers core components (backend, frontend) and detects
    optional components using Python's import system.
    """
    logger.info("Registering component health checks...")

    # Initialize caches once at startup
    initialize_route_metadata_cache()
    initialize_lifecycle_metadata_cache()

    # Register backend component (includes system metrics - CPU, Memory, Disk)
    # Note: Frontend (Flet) is integrated into the Server card, no separate check needed
    register_health_check(ComponentName.BACKEND, backend_component_health)
    logger.info("Backend component health check registered")
    # Register web frontend health check (server-rendered pages at /)
    register_health_check(ComponentName.WEB_FRONTEND, web_frontend_component_health)
    logger.info("Web frontend component health check registered")
    # Register scheduler component health check
    register_health_check(ComponentName.SCHEDULER, scheduler_component_health)

    logger.info("Scheduler component health check registered (with task data)")

    # Register worker health check (shows queue status and job metrics)
    from app.services.system.health_worker import check_worker_health

    register_health_check(ComponentName.WORKER, check_worker_health)
    logger.info("Worker component health check registered")
    # Register cache health check (Redis connectivity and operations)
    from app.services.system.health import check_cache_health

    register_health_check(ComponentName.CACHE, check_cache_health)
    logger.info("Cache component health check registered")
    # Register database health check
    from app.services.system.health_db import check_database_health

    register_health_check(ComponentName.DATABASE, check_database_health)
    logger.info("Database component health check registered")

    # Register ingress health check (Traefik reverse proxy)
    from app.services.system.health import check_ingress_health

    register_health_check(ComponentName.INGRESS, check_ingress_health)
    logger.info("Ingress component health check registered")
    # Register observability health check (Logfire status)
    from app.services.system.health import check_observability_health

    register_health_check(ComponentName.OBSERVABILITY, check_observability_health)
    logger.info("Observability component health check registered")

    logger.info("Component health detection complete")

    # ==========================================
    # Service Health Checks Registration
    # ==========================================

    from app.services.system import health as system_health

    logger.info("Registering service health checks...")
    system_health.register_declared_service_health()

    logger.info("Service health detection complete")

from fastapi import FastAPI

from app.components.backend.api import events as worker_events
from app.components.backend.api import (
    health,
    jobs,
    kept_requests,
    load_test_api,
    metrics,
    ontology,
    pastebox,
    scheduler,
    task_history,
    traffic,
    worker,
)
from app.components.backend.api.database import router as database_router
from app.components.backend.api.deploy.router import router as deploy_router


def include_routers(app: FastAPI) -> None:
    """Include all API routers in the FastAPI app"""
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(jobs.router, prefix="/api/v1")
    app.include_router(kept_requests.router, prefix="/api/v1")
    app.include_router(metrics.router, prefix="/api/v1")
    app.include_router(ontology.router, prefix="/api/v1")
    app.include_router(pastebox.router, prefix="/api/v1")
    app.include_router(traffic.router, prefix="/api/v1")
    app.include_router(load_test_api.router, prefix="/api/v1")
    app.include_router(worker.router, prefix="/api/v1")
    app.include_router(task_history.router, prefix="/api/v1")
    app.include_router(worker_events.router, prefix="/events", tags=["events"])
    app.include_router(scheduler.router, prefix="/api/v1")
    app.include_router(database_router, prefix="/api/v1")
    app.include_router(deploy_router, prefix="/api/v1")

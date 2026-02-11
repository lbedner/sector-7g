from fastapi import FastAPI

from app.components.backend.api import health
from app.components.backend.api import worker
from app.components.backend.api import scheduler
from app.components.backend.api.auth.router import router as auth_router


def include_routers(app: FastAPI) -> None:
    """Include all API routers in the FastAPI app"""
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(worker.router, prefix="/api/v1", tags=["worker"])
    app.include_router(scheduler.router, prefix="/api/v1", tags=["scheduler"])
    app.include_router(auth_router, prefix="/api/v1")
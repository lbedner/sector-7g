# app/components/backend/middleware/docs_auth.py
"""
Auto-discovered HTTP Basic Auth middleware for FastAPI docs endpoints.

Protects /docs, /redoc, and /openapi.json behind HTTP Basic Auth
when DOCS_AUTH_ENABLED=true. Drop-in portable to any Aegis Stack project.
"""

import base64
import secrets

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

PROTECTED_PATHS = {"/docs", "/redoc", "/openapi.json"}


def register_middleware(app: FastAPI) -> None:
    """Auto-discovered middleware registration."""
    if not settings.DOCS_AUTH_ENABLED:
        return

    @app.middleware("http")
    async def docs_basic_auth(request: Request, call_next):  # noqa: N802
        if request.url.path not in PROTECTED_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Basic "):
            try:
                decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
                username, password = decoded.split(":", 1)
                username_ok = secrets.compare_digest(
                    username, settings.DOCS_USERNAME
                )
                password_ok = secrets.compare_digest(
                    password, settings.DOCS_PASSWORD
                )
                if username_ok and password_ok:
                    return await call_next(request)
            except (ValueError, UnicodeDecodeError):
                pass

        return Response(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="API Documentation"'},
        )

"""
Auto-discovered Logfire observability middleware.

Configures Logfire and instruments FastAPI and other enabled components.
When ``LOGFIRE_TOKEN`` is not set, the entire ``register_middleware``
body is a no-op — skipping ``configure()`` and the ``instrument_*()``
calls avoids loading the OpenTelemetry SDK and the in-memory span
batcher, which together add ~150-300 MiB of fixed overhead even with
``send_to_logfire=False``. On a 512 MiB container that is the
difference between healthy and OOM-flapping.

Set ``LOGFIRE_TOKEN`` in ``.env`` to enable.
"""

import os

from fastapi import FastAPI
import logfire

from app.core.config import settings
from app.core.log import logger
from app.core.ontology.exports import otel
from app.core.ontology.model import stack

_configured: bool | None = None
# The process a configuration names when its caller says nothing: the
# webserver, whose middleware discovery reaches here first.
WEBSERVER = "webserver"


def configure_logfire(unit: str = WEBSERVER) -> bool:
    """Configure Logfire + the process-wide instrumentations (HTTPX,
    SQLAlchemy). Returns whether observability is active. Idempotent -
    the bootstrap call in the app factory and the middleware-discovery
    hook both land here.

    Split from ``register_middleware`` so non-web processes (the
    scheduler running background jobs) get the same configuration - a
    span opened in a process that never configured Logfire is silently
    dropped. No-op when ``LOGFIRE_TOKEN`` is empty — the OTEL SDK is
    heavy and serves no purpose without a destination.
    """
    global _configured
    if _configured is not None:
        return _configured
    if not settings.LOGFIRE_TOKEN:
        logger.info("Logfire: token not set — instrumentation disabled")
        _configured = False
        return False

    # Cap the OTEL BatchSpanProcessor before the SDK reads its env.
    # ``setdefault`` so explicit operator overrides in ``.env`` /
    # compose still win. These bounds prevent unbounded memory growth
    # when Logfire is slow or unreachable.
    os.environ.setdefault(
        "OTEL_BSP_MAX_QUEUE_SIZE", str(settings.OTEL_BSP_MAX_QUEUE_SIZE)
    )
    os.environ.setdefault(
        "OTEL_BSP_MAX_EXPORT_BATCH_SIZE",
        str(settings.OTEL_BSP_MAX_EXPORT_BATCH_SIZE),
    )
    os.environ.setdefault(
        "OTEL_BSP_EXPORT_TIMEOUT", str(settings.OTEL_BSP_EXPORT_TIMEOUT)
    )
    os.environ.setdefault(
        "OTEL_BSP_SCHEDULE_DELAY", str(settings.OTEL_BSP_SCHEDULE_DELAY)
    )
    # Who is reporting (``exports.otel``): this process (``unit``) by its
    # own name, in the stack's namespace, so the webserver, the worker
    # and the scheduler of one stack are told apart and kept together.
    identity = otel(stack(), unit)
    os.environ.setdefault(
        "OTEL_RESOURCE_ATTRIBUTES",
        f"service.namespace={identity['service.namespace']}",
    )

    # Hand over the token the guard above just read. Logfire otherwise
    # resolves it from ``os.environ``, which ``.env`` never populates --
    # pydantic-settings loads that file, the process environment does
    # not. The two views then disagree: the guard passes and
    # ``configure()`` raises LogfireConfigError. Under compose the
    # ``env_file`` exports the token for real so both agree, which is
    # why this only shows up outside a container (aegis-stack#1135).
    logfire.configure(
        token=settings.LOGFIRE_TOKEN,
        service_name=identity["service.name"],
        service_version=identity["service.version"],
        environment=identity["deployment.environment.name"],
        send_to_logfire=True,
        console=False,
    )

    # Instrument HTTPX (always -- httpx is a core dependency)
    logfire.instrument_httpx()
    logger.info("Logfire: HTTPX instrumented")

    # Instrument SQLAlchemy/SQLModel (database component enabled)
    try:
        from app.core.db import engine

        logfire.instrument_sqlalchemy(engine=engine)
        logger.info("Logfire: SQLAlchemy instrumented")
    except Exception as e:
        logger.warning(f"Logfire: Could not instrument SQLAlchemy: {e}")

    # Instrument Redis (redis component enabled)
    try:
        logfire.instrument_redis()
        logger.info("Logfire: Redis instrumented")
    except Exception as e:
        logger.warning(f"Logfire: Could not instrument Redis: {e}")

    logger.info("Logfire observability active (sending to Logfire cloud)")
    _configured = True
    return True


# Traced in every process that calls ``install_auto_tracing``.
SERVICE_MODULES = ("app.services",)


def install_auto_tracing(*modules: str, unit: str = WEBSERVER) -> None:
    """Span every call slower than 10ms in the services, plus ``modules``.

    The generic answer to "instrument the business logic": Logfire's
    import hook wraps whole module trees, so a scheduled job or an API
    request renders as nested service-function spans with their SQL
    children - no hand-placed decorators. MUST run before the traced
    packages are imported, which is why the app factory module and the
    worker and scheduler entrypoints call this at the top, before their
    own app imports.

    The web process passes ``app.components.frontend`` because the UI
    builds server-side in the SAME event loop as the API: a slow view
    build blocks every in-flight request, and without spans there that
    stall is a 4-second hole in the trace with no visible culprit. The
    worker and scheduler never import the UI, so they pass nothing.
    ``unit`` is the process: what its traces report as their service.
    """
    if not configure_logfire(unit):
        return
    import logfire

    traced = [*SERVICE_MODULES, *modules]
    logfire.install_auto_tracing(
        modules=traced,
        min_duration=0.01,
        check_imported_modules="warn",
    )
    logger.info(f"Logfire: auto-tracing {' + '.join(traced)} (>=10ms spans)")


def register_middleware(app: FastAPI) -> None:
    """Middleware-discovery hook: configure the process, then add the
    web-only FastAPI instrumentation on top."""
    if not configure_logfire():
        return
    import logfire

    logfire.instrument_fastapi(app, excluded_urls="/health/.*|/dashboard/.*")
    logger.info("Logfire: FastAPI instrumented")

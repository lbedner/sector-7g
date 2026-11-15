# app/core/config.py
"""
Application configuration management using Pydantic's BaseSettings.

This module centralizes application settings, allowing them to be loaded
from environment variables for easy configuration in different environments.
"""

from typing import Annotated, Literal

from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict

from app.core.configurable import Configurable, asgi_engines, event_loops, timezones
from app.core.constants import DEV_ENVS, AppEnv, ComponentName, QueueName
from app.core.queue_workers import DEFAULT_QUEUES, QueueWorker
from app.core.settings_base import SettingsBase

# Default placeholder bundled with the template — anyone reading the
# template source knows this value, so leaving it unchanged in a non-dev
# deploy would let an attacker forge JWTs. Pinned as a module constant
# so the startup guard below has a single source of truth and a renamed
# placeholder doesn't accidentally bypass the check.
_SECRET_KEY_PLACEHOLDER = "change-this-secret-key-in-production-use-env-variable"
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class Settings(
    SettingsBase,
):
    """
    Defines application settings.
    `model_config` is used to specify that settings should be loaded from a .env file.
    """

    # Project identity
    PROJECT_NAME: str = "sector-7g"
    # Friendly display name for humans (email FROM/body, browser titles);
    # PROJECT_NAME above is the URL-safe slug. Override via env var.
    PROJECT_DISPLAY_NAME: str = "sector-7g"

    # Public-facing base URL (used to build absolute links in outgoing
    # emails - receipts, password reset, subscription welcome, etc.).
    # Override per environment via .env (e.g. https://app.your-domain.com);
    # the localhost default keeps dev working without configuration.
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # Application environment: "dev" or "prod"
    APP_ENV: str = AppEnv.DEV

    # API docs auth (HTTP Basic). When both are set, /docs /redoc /openapi.json
    # require these creds. When unset: open in dev, 404 in any other APP_ENV.
    DOCS_USERNAME: str = ""
    DOCS_PASSWORD: str = ""

    # Public signup gate. When False, /register returns 403 and OAuth new-user
    # creation is refused. Existing users still sign in normally.
    REGISTRATION_ENABLED: Annotated[
        bool,
        Configurable(
            "service_auth", "Whether anyone can sign up; off, an admin makes accounts"
        ),
    ] = True

    # Log level for the application
    LOG_LEVEL: Annotated[
        str,
        Configurable(
            ComponentName.BACKEND,
            "Lowest level a log line is written at",
            choices=lambda: LOG_LEVELS,
        ),
    ] = "INFO"

    # Port for the web server
    PORT: int = 8000

    # The host port compose published: ``make serve`` shifts it when 8000 is
    # taken, writing ``.env.ports``, while the container stays on PORT. A CLI
    # command on the host calling this app's API needs this one. None if unshifted.
    WEBSERVER_HOST_PORT: int | None = None

    # Where this app's own CLI reaches its API. Left empty it follows the
    # published port, so a project served anywhere needs no extra
    # configuration; set it explicitly for a container or a tunnel.
    API_BASE_URL: str = ""

    @property
    def is_dev(self) -> bool:
        """Whether this is a development environment (``DEV_ENVS``)."""
        return self.APP_ENV.lower() in DEV_ENVS

    @property
    def is_docker(self) -> bool:
        """Detect if running inside Docker container."""
        import os

        return os.path.exists("/.dockerenv") or bool(os.getenv("DOCKER_CONTAINER"))

    @model_validator(mode="after")
    def _default_api_base_url(self) -> "Settings":
        """Point the CLI at wherever this app is actually reachable."""
        if not self.API_BASE_URL:
            # In a container, the webserver by name on its own port (not the host's).
            docker = f"webserver:{self.PORT}" if self.is_docker else None
            local = f"localhost:{self.WEBSERVER_HOST_PORT or self.PORT}"
            self.API_BASE_URL = f"http://{docker or local}"
        return self

    # Development settings
    AUTO_RELOAD: bool = False

    # ASGI server: `make serve ENGINE=granian` for one run, a deployment's env
    # file for good, or saved in the Overseer, which the entrypoint reads first.
    WEBSERVER_ENGINE: Annotated[
        Literal["uvicorn", "granian"],
        Configurable(
            ComponentName.BACKEND,
            "ASGI server the webserver runs on",
            choices=asgi_engines,
        ),
    ] = "uvicorn"

    # Event loop, a separate axis from the engine. "auto" resolves to
    # uvloop when installed; it never resolves to rloop on its own.
    WEBSERVER_LOOP: Annotated[
        Literal["auto", "asyncio", "uvloop", "rloop", "zuvloop"],
        Configurable(
            ComponentName.BACKEND,
            "Event loop the webserver runs on",
            choices=event_loops,
        ),
    ] = "auto"

    # Docker settings (used by docker-compose)
    AEGIS_STACK_TAG: str = "sector-7g:latest"
    AEGIS_STACK_VERSION: str = "dev"
    # Deployed commit, stamped by ``aegis deploy``; cached payloads are
    # namespaced by it. See ``services/insights/constants.py``.
    BUILD_ID: str = "dev"
    # Stamped too: a server has no ``.aegis/deploy.yml`` to read its address from.
    SERVER_HOST: str | None = None

    # Health monitoring: checks answer on /health/ for any monitor to poll
    HEALTH_CHECK_TIMEOUT_SECONDS: Annotated[
        float,
        Configurable(
            "health", "Seconds a health check waits before calling a component down"
        ),
    ] = 2.0
    SYSTEM_METRICS_CACHE_SECONDS: Annotated[
        int,
        Field(ge=1),
        Configurable(
            "health",
            "Seconds the host's CPU, memory and disk readings are reused (at least one: CPU is read as its share since the last read)",
        ),
    ] = 5

    MEMORY_THRESHOLD_PERCENT: Annotated[
        float,
        Configurable(
            "health",
            "Memory in use, percent, at which the host or a container is unhealthy",
        ),
    ] = 90.0
    DISK_THRESHOLD_PERCENT: Annotated[
        float,
        Configurable("health", "Disk in use, percent, at which the host is unhealthy"),
    ] = 85.0
    CPU_THRESHOLD_PERCENT: Annotated[
        float,
        Configurable(
            "health",
            "CPU in use, percent, at which the host or a container is unhealthy",
        ),
    ] = 95.0
    WARNING_PERCENT_OF_THRESHOLD: Annotated[
        float,
        Configurable(
            "health",
            "Where a warning starts, as a percent of the memory, disk and CPU thresholds",
        ),
    ] = 80.0

    # Where stored objects live: chat attachments, documents, anything
    # addressed by content hash. A directory today; the storage component
    # points this at a bucket without any caller noticing.
    STORAGE_ROOT: str = "storage_data"
    # Which backend get_storage() builds: the storage component flips this
    # to a bucket; everything else keeps the directory above.
    STORAGE_BACKEND: str = "filesystem"

    # Where the scheduled backup job writes dumps. A relative path resolves
    # against the process cwd, which inside a container is the writable
    # layer - fine for local dev, but there the dumps are destroyed by the
    # next `up --force-recreate`, i.e. every deploy. The Dockerfile points
    # every container at the mounted backup volume so dumps outlive them.
    DATABASE_BACKUP_DIR: str = "backups"
    DATABASE_BACKUP_KEEP: Annotated[
        int,
        Configurable(ComponentName.DATABASE, "Backups kept; older ones are removed"),
    ] = 7

    # Off-site backup (app.services.system.offsite), from .env or the store.
    OFFSITE_BACKUP_REPOSITORY: str | None = None
    OFFSITE_BACKUP_PASSWORD: str | None = None
    OFFSITE_BACKUP_ACCESS_KEY: str | None = None
    OFFSITE_BACKUP_SECRET_KEY: str | None = None

    # Flet frontend settings
    FLET_ASSETS_DIR: str = "assets"  # Directory for Flet static assets (images, etc.)

    # Web frontend settings (server-rendered pages at /). Both paths are
    # relative to the project root; the static dir holds the sources, and a
    # build writes fingerprinted output into its ``dist/`` subdirectory.
    WEB_TEMPLATES_DIR: str = "app/components/web_frontend/templates"
    WEB_STATIC_DIR: str = "app/components/web_frontend/static"
    # One line on the project: the landing hero and its SEO description.
    PROJECT_DESCRIPTION: str = (
        "A production-ready async Python application built with Aegis Stack"
    )
    WEB_THEME: str = "aegis"  # the Overseer's theme: a file in web_frontend/themes/
    OVERSEER_CODE_ENABLED: Annotated[
        bool,
        Configurable(
            ComponentName.WEB_FRONTEND,
            "Show the project's source on Overseer > Code outside dev (admins only)",
        ),
    ] = False
    OVERSEER_DATABASE_ROWS_ENABLED: Annotated[
        bool,
        Configurable(
            ComponentName.WEB_FRONTEND,
            "Show the tables' rows on Overseer > Database outside dev (admins only)",
        ),
    ] = False

    # Authentication settings
    # Without the auth service (or set false in .env) a dev user is synthesized
    AUTH_ENABLED: bool = False
    AUTH_LEVEL: str = "none"
    DEV_USER_ROLE: str = "admin"  # Role for synthetic dev user when AUTH_ENABLED=false
    # Email allowlist for ``require_admin`` — gates operator-only routes
    # (refund actions, dispute review, aggregate revenue charts, etc.).
    # Empty list 403s everyone when ``AUTH_ENABLED=True``; safe default
    # before someone deliberately grants themselves admin. Set in
    # ``.env`` as a JSON list: ``ADMIN_USER_EMAILS=["you@example.com"]``.
    ADMIN_USER_EMAILS: list[str] = []
    INVITE_ACCEPTANCE_MODE: str = (
        "email"  # "email" requires email match, "token" allows anyone with token
    )
    SECRET_KEY: str = _SECRET_KEY_PLACEHOLDER
    # Distinct secret for column-level at-rest encryption (AES-GCM v2 in
    # ``app/core/encryption.py``). Splits JWT-signing and credential-
    # encryption blast radii so leaking one secret doesn't compromise
    # both. When unset, encryption.py falls back to ``SECRET_KEY`` with
    # a one-time warning. Set in ``.env`` for production deploys.
    ENCRYPTION_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: Annotated[
        int, Configurable("service_auth", "Minutes a sign-in's access token lasts")
    ] = 15
    # Dev-only multiplier on ``ACCESS_TOKEN_EXPIRE_MINUTES``. When
    # ``APP_ENV == "dev"``, the effective session length becomes
    # ``ACCESS_TOKEN_EXPIRE_MINUTES * DEV_TOKEN_EXPIRE_MULTIPLIER`` so
    # devs aren't logged out every 15 minutes during iteration. Prod /
    # staging are unaffected (the multiplier doesn't fire). Override in
    # ``.env`` if 4x isn't enough — e.g. ``DEV_TOKEN_EXPIRE_MULTIPLIER=16``.
    DEV_TOKEN_EXPIRE_MULTIPLIER: int = 4
    REFRESH_TOKEN_EXPIRE_DAYS: Annotated[
        int, Configurable("service_auth", "Days before a session has to sign in again")
    ] = 14
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24

    # Rate limiting settings
    RATE_LIMIT_LOGIN_MAX: Annotated[
        int,
        Configurable(
            "service_auth", "Sign-in attempts one address may make per window"
        ),
    ] = 5
    RATE_LIMIT_LOGIN_WINDOW: Annotated[
        int, Configurable("service_auth", "Seconds the sign-in limit counts over")
    ] = 60
    RATE_LIMIT_REGISTER_MAX: Annotated[
        int,
        Configurable(
            "service_auth",
            "Sign-ups or password resets one address may ask for per window",
        ),
    ] = 3
    RATE_LIMIT_REGISTER_WINDOW: Annotated[
        int, Configurable("service_auth", "Seconds the sign-up limit counts over")
    ] = 60
    # Resend-verification is a user-initiated button; a tighter-than-register
    # limit would feel punishing during legit retries. 3 per 5 min strikes
    # the balance — still spam-proof, far less fiddly.
    RATE_LIMIT_RESEND_VERIFICATION_MAX: Annotated[
        int,
        Configurable(
            "service_auth", "Verification emails one address may ask for per window"
        ),
    ] = 3
    RATE_LIMIT_RESEND_VERIFICATION_WINDOW: Annotated[
        int,
        Configurable(
            "service_auth", "Seconds the verification-email limit counts over"
        ),
    ] = 300

    # Account lockout settings
    ACCOUNT_LOCKOUT_ATTEMPTS: Annotated[
        int, Configurable("service_auth", "Failed sign-ins before an account is locked")
    ] = 5
    ACCOUNT_LOCKOUT_MINUTES: Annotated[
        int, Configurable("service_auth", "Minutes a locked account stays locked")
    ] = 15

    TRUST_PROXY_HEADERS: bool = (
        False  # Behind a reverse proxy: the client comes from X-Forwarded-For
    )
    TRUSTED_PROXIES: list[str] = [
        "127.0.0.1",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]  # Senders believed (Traefik's ranges); never "*", which believes the caller

    # Traffic monitor: per-source request-volume visibility ("who's hammering
    # you") rendered in Overseer. Counts requests per client IP, bucketed
    # hourly; backed by Redis when present (shared across processes), in-memory
    # otherwise (per-process, resets on restart).
    TRAFFIC_MONITOR_ENABLED: Annotated[
        bool,
        Configurable(
            ComponentName.BACKEND,
            "Count requests per client address, for the Server page's traffic",
        ),
    ] = True
    # Trailing window the Overseer panel ranks sources over (hours).
    TRAFFIC_WINDOW_HOURS: Annotated[
        int,
        Configurable(
            ComponentName.BACKEND, "Hours of traffic the Server page ranks sources over"
        ),
    ] = 24
    # Read-time dominance flag: a single source over this share of windowed
    # traffic (and clearing the absolute floor) is highlighted as "hammering."
    TRAFFIC_DOMINANCE_SHARE: Annotated[
        float,
        Configurable(
            ComponentName.BACKEND,
            "Share of all traffic (0 to 1) that flags one source as hammering",
        ),
    ] = 0.5
    TRAFFIC_DOMINANCE_FLOOR: Annotated[
        int,
        Configurable(
            ComponentName.BACKEND,
            "Fewest requests a source needs before it can be flagged",
        ),
    ] = 100

    # HttpOnly session cookie holding the JWT after login / register /
    # OAuth callback. None = auto (off in dev, on otherwise). Set to
    # False to run prod over HTTP without TLS — browsers refuse Secure
    # cookies on insecure origins. Read by ``set_session_cookie`` in
    # ``app.core.security``, which fires for every browser-side auth
    # surface (not just OAuth), so this setting must exist whenever
    # ``include_auth`` is true.
    SESSION_COOKIE_SECURE: bool | None = None

    # Redis settings for arq background tasks
    REDIS_URL: str = "redis://redis:6379"  # Docker service name by default
    REDIS_URL_LOCAL: str | None = None  # Manual override for local CLI usage
    # Host publish port chosen by `make serve` (loaded from .env.ports).
    # None = use the container port. See `localhost_url`.
    REDIS_HOST_PORT: int | None = None
    REDIS_DB: int = 0
    # Logical Redis DB for the application cache (view caches, bulk
    # caches, etc.). Separate from REDIS_DB so ``cache.clear()`` can't
    # accidentally nuke arq's queue (which lives on REDIS_DB) and so a
    # FLUSHDB against either namespace doesn't take the other down.
    CACHE_REDIS_DB: int = 1

    @property
    def redis_url_effective(self) -> str:
        """Get effective Redis URL, preferring local override when not in Docker."""
        if self.REDIS_URL_LOCAL and not self.is_docker:
            return self.REDIS_URL_LOCAL
        if not self.is_docker:
            return self.localhost_url(self.REDIS_URL, {"redis"}, self.REDIS_HOST_PORT)
        return self.REDIS_URL

    # Worker settings; per-queue ones are modelled in app/core/queue_workers.py
    WORKER_QUEUES: dict[str, QueueWorker] = Field(default_factory=DEFAULT_QUEUES.copy)
    WORKER_QUEUE_DEFAULT: QueueWorker = QueueWorker()
    # Not on Overseer > Settings: arq reads both in its queue classes, before saved values apply
    WORKER_KEEP_RESULT_SECONDS: int = 3600  # Keep job results for 1 hour
    WORKER_MAX_TRIES: int = 3
    # Poison-message guard: drop a Redis-stream message redelivered past this
    # many times, so a task that kills its worker every run (OOM/SIGKILL never
    # acks, so xautoclaim re-yields it forever) can't loop and re-bill paid
    # work. 0 disables the guard.
    WORKER_MAX_REDELIVERIES: Annotated[
        int,
        Configurable(
            ComponentName.WORKER,
            "Redeliveries before a job that keeps killing its worker is dropped (0: never)",
        ),
    ] = 5

    # Redis connection settings for arq workers
    REDIS_CONN_TIMEOUT: int = 5  # Connection timeout in seconds (default: 1)
    REDIS_CONN_RETRIES: int = 5  # Connection retry attempts (default: 5)
    REDIS_CONN_RETRY_DELAY: int = 1  # Delay between retries (default: 1)

    # Worker health check settings
    WORKER_HEALTH_CHECK_INTERVAL: int = 15  # In seconds (default: 15)

    # Task history retention (Redis Hashes auto-expire after this)
    TASK_HISTORY_TTL_SECONDS: Annotated[
        int, Configurable(ComponentName.WORKER, "Seconds a job's history is kept")
    ] = 86400  # 24 hours

    # Database settings
    DATABASE_SLOW_TRANSACTION_SECONDS: Annotated[
        float,
        Configurable(
            ComponentName.DATABASE,
            "A transaction held this long is recorded on the Database page, seconds (0: off)",
        ),
    ] = 2.0

    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/sector-7g"
    DATABASE_URL_LOCAL: str | None = None  # Manual override for local CLI usage
    # Host publish port chosen by `make serve` (loaded from .env.ports).
    # None = use the container port. See `localhost_url`.
    POSTGRES_HOST_PORT: int | None = None
    DATABASE_ENGINE_ECHO: bool = False

    @property
    def database_url_effective(self) -> str:
        """Get effective database URL, preferring local override when not in Docker."""
        if self.DATABASE_URL_LOCAL and not self.is_docker:
            return self.DATABASE_URL_LOCAL
        if not self.is_docker:
            return self.localhost_url(
                self.DATABASE_URL, {"postgres"}, self.POSTGRES_HOST_PORT
            )
        return self.DATABASE_URL

    # Web search (app/core/search.py; an agent's web_search tool), unset = off.
    BRAVE_SEARCH_API_KEY: str | None = None  # https://brave.com/search/api/
    # Porkbun registrar API keys — used by the `dns` CLI and by ``app/services/ops/``
    # to read and write DNS records. Grab them at porkbun.com/account/api. Strongly
    # recommend the per-domain "API ACCESS" toggle inside each domain's detail page
    # (porkbun.com -> Domain Management -> click the domain -> toggle API ACCESS on)
    # so the master key's blast radius is limited to the domains you've enabled.
    PORKBUN_API_KEY: str | None = None
    PORKBUN_SECRET_KEY: str | None = None

    # Apex domain managed by the registrar adapter. Used by the `dns` CLI as the default
    # -d/--domain so commands like `dns set app` know which registered domain to touch.
    # Leave unset and the CLI errors with a clear message.
    BASE_DOMAIN: str | None = None

    HCLOUD_TOKEN: str | None = None  # aegis deploy-agent's, one per provider
    DIGITALOCEAN_TOKEN: str | None = None
    CLOUDFLARE_API_TOKEN: str | None = None  # names a server by DNS

    # Observability (Logfire)
    # Set LOGFIRE_TOKEN to enable sending traces to Logfire cloud
    # Get a write token from https://logfire.pydantic.dev (Project Settings > Write Tokens)
    LOGFIRE_TOKEN: str | None = None

    # Read token for Logfire Query API (enables trace analytics in the Overseer dashboard)
    # Get from: Project Settings > Read Tokens in Logfire
    LOGFIRE_READ_TOKEN: str | None = None

    # Logfire project URL for linking to the dashboard
    # e.g. "https://logfire.pydantic.dev/myorg/myproject"
    LOGFIRE_PROJECT_URL: str | None = None

    # OTEL span buffer limits. The default ``BatchSpanProcessor``
    # config (2048-span queue, no export timeout) keeps failed
    # Logfire export batches in memory forever when the cloud is
    # slow or unreachable — the container leaks until OOM. These
    # caps backstop that. ``logfire_tracing.register_middleware``
    # mirrors them into ``os.environ`` so the OTEL SDK actually
    # sees them.
    OTEL_BSP_MAX_QUEUE_SIZE: int = 1024
    OTEL_BSP_MAX_EXPORT_BATCH_SIZE: int = 256
    OTEL_BSP_EXPORT_TIMEOUT: int = 10000  # ms
    OTEL_BSP_SCHEDULE_DELAY: int = 5000  # ms

    # Scheduler settings: an IANA timezone name, which cron triggers inherit
    SCHEDULER_TIMEZONE: Annotated[
        str,
        Configurable(
            ComponentName.SCHEDULER, "Timezone scheduled jobs run in", choices=timezones
        ),
    ] = "UTC"

    # Traefik Ingress settings
    TRAEFIK_API_URL: str = "http://traefik:8080"  # Docker service name
    TRAEFIK_API_URL_LOCAL: str | None = None  # Manual override for local CLI usage
    # Host publish port chosen by `make serve` (loaded from .env.ports).
    # None = use the container port. See `localhost_url`.
    INGRESS_DASHBOARD_PORT: int | None = None

    @staticmethod
    def localhost_url(
        url: str, docker_hostnames: set[str], host_port: int | None = None
    ) -> str:
        """Rewrite a Docker-network URL for access from the host.

        Swaps a Docker service hostname (e.g. ``postgres``) for
        ``localhost`` and, when ``make serve`` chose a non-default host
        publish port (a ``*_HOST_PORT`` loaded from ``.env.ports``), swaps
        the container port for it. ``make serve`` shifts only the host
        publish port when the default is taken by another stack, so a
        host-side CLI command must use that chosen port, not the container
        port. Returns ``url`` unchanged when its host is not one of
        ``docker_hostnames`` (already host-reachable). Auth and path are
        preserved.
        """
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(url)
        if parsed.hostname not in docker_hostnames:
            return url
        netloc = "localhost"
        if parsed.username:
            if parsed.password:
                netloc = f"{parsed.username}:{parsed.password}@localhost"
            else:
                netloc = f"{parsed.username}@localhost"
        port = host_port or parsed.port
        if port:
            netloc = f"{netloc}:{port}"
        return urlunparse(parsed._replace(netloc=netloc))

    @property
    def traefik_api_url_effective(self) -> str:
        """
        Get effective Traefik API URL.

        Prefers local override when not in Docker.
        """
        if self.TRAEFIK_API_URL_LOCAL and not self.is_docker:
            return self.TRAEFIK_API_URL_LOCAL
        if not self.is_docker:
            return self.localhost_url(
                self.TRAEFIK_API_URL, {"traefik"}, self.INGRESS_DASHBOARD_PORT
            )
        return self.TRAEFIK_API_URL

    # ``.env.ports`` carries the host publish ports `make serve` chose for
    # this run (gitignored, regenerated each run). Listed after ``.env`` so
    # its values win for the keys it defines; both are optional at load time.
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.ports"), env_file_encoding="utf-8"
    )

    @model_validator(mode="after")
    def _guard_against_placeholder_secret_in_prod(self) -> "Settings":
        """Refuse to boot a prod-shaped deploy with the template SECRET_KEY.

        Anyone reading the public template knows this value, so leaving it
        unchanged would let an attacker forge JWTs against the deploy. We
        only enforce when APP_ENV != "dev" so local development keeps
        working without forcing every contributor to set the env var.
        """
        if self.APP_ENV != "dev" and self.SECRET_KEY == _SECRET_KEY_PLACEHOLDER:
            raise ValueError(
                "SECRET_KEY is set to the template placeholder. Generate a "
                "random value (e.g. `python -c 'import secrets;"
                " print(secrets.token_urlsafe(64))'`) and set it via the "
                "SECRET_KEY env var before booting outside dev."
            )
        return self

    def reload(self) -> None:
        """
        Reload settings from .env file in place.

        Updates all field values from a fresh Settings instance,
        allowing configuration changes to take effect without restart.
        """
        # Create a fresh Settings instance that reads from .env
        new_settings = Settings()

        # Update all field values in place
        for field_name in self.model_fields:
            setattr(self, field_name, getattr(new_settings, field_name))


settings = Settings()


def reload_settings() -> None:
    """
    Reload the global settings instance from .env file.

    Call this after modifying the .env file to pick up changes
    without restarting the application.
    """
    settings.reload()


# Pure arq queue helper functions - use dynamic discovery
def get_available_queues() -> list[str]:
    """Get all available queue names via dynamic discovery."""
    try:
        from app.components.worker.registry import discover_worker_queues

        queues: list[str] = discover_worker_queues()
        return queues
    except ImportError:
        # Worker components not available
        return []


def get_default_queue() -> str:
    """The queue a task goes to when none is named: the stack's own."""
    return QueueName.SYSTEM


def is_valid_queue(queue_name: str) -> bool:
    """Check if a queue name is valid."""
    try:
        from app.components.worker.registry import validate_queue_name

        result: bool = validate_queue_name(queue_name)
        return result
    except ImportError:
        # Worker components not available, no queues are valid
        return False

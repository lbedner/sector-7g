# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sector-7g is a production-ready async Python 3.14 application built with the Aegis Stack template. It runs as a Docker Compose multi-service architecture with FastAPI backend, Flet frontend dashboard, arq workers (Redis-backed), APScheduler, PostgreSQL, and Traefik reverse proxy.

## Common Commands

### Development Workflow
```bash
make serve          # Build and start all services (Docker)
make rebuild        # Rebuild image then serve
make refresh        # Nuclear reset: clean everything, rebuild, serve
make restart        # Stop and serve (no rebuild)
make stop           # Gracefully stop all services
```

### Code Quality
```bash
make lint           # Ruff linting (ruff check .)
make fix            # Auto-fix lint + format (ruff check --fix && ruff format)
make typecheck      # Type checking with ty
make check          # All checks: lint + typecheck + test
```

### Testing
```bash
make test           # Run pytest
make test-verbose   # Verbose pytest output
uv run pytest tests/test_core.py           # Single test file
uv run pytest tests/test_core.py::test_fn  # Single test function
```

### Database
```bash
make migrate        # Apply Alembic migrations (runs inside Docker)
make migrate-check  # Show migration status
make db-fresh       # Nuclear DB reset (drops volume + restarts)
```

### Logs & Debugging
```bash
make logs           # Follow all service logs
make logs-web       # Webserver logs only
make logs-worker    # Worker logs only
make shell          # Bash inside webserver container
```

### Dependencies
```bash
uv sync --all-extras   # Install all deps (dev, docs)
```

### CLI
```bash
sector-7g health check --detailed   # Component health status
sector-7g --help                    # All available commands
```

## Architecture

### Service Composition (Docker)
All services run via Docker Compose with dev/prod profiles:
- **webserver** (port 8000) — FastAPI + Flet dashboard mounted at `/dashboard`
- **scheduler** — APScheduler with PostgreSQL-persisted jobs
- **worker-inanimate-rod** — arq worker for Inanimate Carbon Rod (system maintenance + simulation)
- **worker-homer** — arq worker for Homer's tasks (low concurrency, CPU-bound)
- **worker-lenny** — arq worker for Lenny's tasks (high concurrency, I/O-bound)
- **worker-carl** — arq worker for Carl's tasks (high concurrency, I/O-bound)
- **worker-charlie** — arq worker for Charlie's tasks (moderate concurrency, I/O-bound)
- **worker-grimey** — arq worker for Frank Grimes (deceased, one task at a time)
- **postgres** — PostgreSQL 16
- **redis** — Redis 7 (task queue + cache)
- **traefik** — Reverse proxy (port 80, dashboard at 8080)

### Code Layout
```
app/
├── core/              # Settings (Pydantic), DB engines, logging, security
├── models/            # SQLModel table definitions
├── components/
│   ├── backend/       # FastAPI app: api/, middleware/, startup/, shutdown/
│   ├── frontend/      # Flet UI: dashboard cards, modals, diagram views
│   ├── scheduler/     # APScheduler initialization + job definitions
│   └── worker/        # arq queues/ (WorkerSettings per queue) + tasks/
├── services/          # Business logic: auth, scheduler, system monitoring
├── cli/               # Typer CLI (health, auth, tasks, docs)
├── integrations/      # App composition (creates integrated Flet+FastAPI app)
└── entrypoints/       # Process entry points: webserver.py, scheduler.py
```

### Key Patterns

**Configuration**: `app/core/config.py` uses Pydantic `BaseSettings` loaded from `.env`. Docker service hostnames (redis, postgres, traefik) auto-translate to localhost when running outside Docker.

**Database**: Dual engine setup in `app/core/db.py` — sync engine for Alembic/CLI, async engine (asyncpg) for web requests. Use `db_session()` for sync, `get_async_session()` for async.

**Workers**: Pure arq patterns — each queue has its own `WorkerSettings` class in `app/components/worker/queues/`. Tasks are plain async functions in `worker/tasks/`. See `app/components/worker/CLAUDE.md` for detailed worker development guide.

**API routes**: Registered in `app/components/backend/api/routing.py`. Endpoints live under `api/health.py`, `api/auth/`, `api/worker.py`, `api/scheduler.py`.

**Frontend**: Flet dashboard with three views (Stack, Cards, Diagram). Auto-refreshes from `/health/` endpoint every 30 seconds.

**Logging**: Structlog — colored console in dev, JSON in prod. Configured in `app/core/log.py`.

### Ruff Configuration
- Line length: 88
- Rules: E, F, I, N, W, UP (pyupgrade for modern Python syntax)
- First-party package: `app`

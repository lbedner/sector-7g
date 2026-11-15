# sector-7g

A production-ready async Python application built with Aegis Stack

## What It Is Made Of

<!-- what-it-has -->
### Components

- **Backend**: FastAPI on uvicorn or granian, lifecycle hooks, in-memory request metrics, API load testing for every route (FastAPI on PORT (default 8000); OpenAPI docs at /docs)
- **Frontend**: Flet, ships with the Overseer system dashboard (Flet dashboard at /dashboard)
- **Worker**: Pluggable Arq, Taskiq, or Dramatiq (`make logs-worker`; tasks under app/worker, CLI group `tasks`)
- **Scheduler**: APScheduler with persistent jobs (Runs in-process; jobs listed on the dashboard)
- **Database**: Postgres (self-hosted or Neon serverless) or SQLite + SQLModel ORM (`make migrate` runs Alembic; models under app/models)
- **Redis**: Redis for caching, sessions, pub/sub (redis:6379 in the compose network; REDIS_URL from the host)
- **Ingress**: Traefik v3 reverse proxy with TLS (Traefik in front of the app; routes from docker-compose labels)
- **Observability**: Pydantic Logfire tracing + metrics + logging (Logfire tracing; `make logs` for the raw stream)
- **Web Frontend**: Server-rendered pages at `/`: Jinja2 + htmx + Alpine, Tailwind/DaisyUI styling (Server-rendered pages at /)
- **Deploy**: Deployment target (Docker Compose), read by the Overseer (`aegis deploy`; the socket-proxy service answers the Overseer's read-only Docker queries)

Each part's routes, jobs and tables: the docs' *What It Is Made Of* page (`stack.md`), read from the code when the docs are built.
<!-- /what-it-has -->

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Install dependencies:**
   ```bash
   uv sync                    # Core dependencies only
   # Or for development: uv sync  (includes testing, linting, docs)
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. **No `make`?** Every `make <target>` in this README also runs as
   `uv run poe <target>` — same tasks, no make needed, which is how
   Windows gets through the rest of this page. `uv run poe -h` lists
   them.

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database:**
   ```bash
   # The postgres service starts with `make serve` (docker compose).
   # Tables are created via Alembic migrations on first run.
   ```

6. **Run the application:**
   ```bash
   make serve
   ```

The application will be available at `http://127.0.0.1:8000`. If port 8000 is
already taken, `make serve` picks the next free port and prints the URL it
chose, so two stacks can run side by side without editing any config.

Every command in this README also works as `uv run poe <target>` (for
example `uv run poe serve`), once the dev dependencies are installed
(`uv sync`); run `uv run poe -h` for the full list.

## Development

### Running Tests
```bash
make test
```

### Code Quality
```bash
make check  # Run linting, type checking, and tests
```

### CLI Commands

Your project gets its own CLI command **automatically installed** when first used - no setup required! 

```bash
# Health monitoring (auto-installs CLI if needed)
make health                     # Basic health check
make health-detailed            # Detailed component status
make health-json               # JSON output for scripts
make health-quick              # Quick healthy/unhealthy check

# Direct CLI usage (after first make command)
sector-7g health check              # Basic health check
sector-7g health check --detailed   # Detailed component status
sector-7g health check --json       # JSON output for scripts
sector-7g health quick              # Quick healthy/unhealthy check

# Explore all commands
sector-7g --help                    # See all available commands
sector-7g health --help             # See health subcommand options
```

**Environment Issues?** If CLI commands don't work:
```bash
# Ensure you're in the project's virtual environment
unset VIRTUAL_ENV               # Clear Docker contamination
source .venv/bin/activate       # Activate local venv
make health                     # This will auto-install CLI
# Or manually: make install-cli
```

### Documentation
```bash
make docs-serve  # Serve docs at http://localhost:8001/sector-7g/
```

## Docker

### Development
```bash
docker compose --profile dev up
```

### Production
```bash
docker compose --profile prod up
```

## Configuration

### Database Settings

The database component uses PostgreSQL with the following default configuration:

```bash
# Environment variables (add to .env file)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/sector-7g
DATABASE_ENGINE_ECHO=false                  # Enable SQL query logging
```

### Database Usage

```python
from app.core.db import db_session
from sqlmodel import SQLModel, Field, select

# Define a model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str

# Use the database
with db_session() as session:
    user = User(name="John Doe", email="john@example.com")
    session.add(user)
    # Auto-committed by context manager
```

## Project Structure

```
sector-7g/
├── app/                    # Application code
│   ├── components/         # Component implementations
│   │   ├── backend/       # FastAPI backend
│   │   └── frontend/      # Flet frontend
│   │   └── scheduler/     # APScheduler background tasks
│   ├── cli/               # CLI commands and health monitoring
│   ├── core/              # Core utilities
│   │   ├── config.py      # Environment-dependent configuration
│   │   ├── constants.py   # Immutable constants (12-Factor App)
│   │   ├── db.py          # Database connection and session management
│   │   └── log.py         # Structured logging
│   ├── entrypoints/       # Execution entry points
│   ├── integrations/      # App composition layer
├── tests/                 # Test suite
├── docs/                  # Documentation
├── docker-compose.yml     # Docker services
└── pyproject.toml        # Project configuration
```

---

Generated with [Aegis Stack](https://github.com/lbedner/aegis-stack)
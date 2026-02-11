# Worker Component Development Guide

This guide covers arq worker architecture patterns and development for the sector-7g worker component.

## Worker Architecture (arq)

sector-7g uses pure **arq patterns** without custom wrappers, following native arq CLI and configuration patterns.

### Worker Configuration Structure

Each worker queue has its own `WorkerSettings` class:
- `app/components/worker/queues/inanimate_rod.py` - Inanimate Carbon Rod (system maintenance + simulation)
- `app/components/worker/queues/homer.py` - Homer Simpson worker (CPU-bound, low concurrency)
- `app/components/worker/queues/lenny.py` - Lenny Leonard worker (I/O-bound, high concurrency)
- `app/components/worker/queues/carl.py` - Carl Carlson worker (I/O-bound, high concurrency)
- `app/components/worker/queues/charlie.py` - Charlie, plant worker (I/O-bound, moderate concurrency)
- `app/components/worker/queues/grimey.py` - Frank Grimes, deceased (meticulous, max_jobs=1)

### Worker Services in Docker

Workers run as separate Docker services with specific names:
- **`worker-inanimate-rod`** - Inanimate Carbon Rod: system maintenance + simulation (max_jobs=15)
- **`worker-homer`** - Homer's tasks: donuts, naps, safety checks (max_jobs=3, CPU-bound)
- **`worker-lenny`** - Lenny's tasks: diagnostics, inspections, reports (max_jobs=15, I/O-bound)
- **`worker-carl`** - Carl's tasks: inspectors, reports, handoffs (max_jobs=15, I/O-bound)
- **`worker-charlie`** - Charlie's tasks: gauges, restocking, shift notes (max_jobs=10, I/O-bound)
- **`worker-grimey`** - Frank Grimes (deceased): meticulous audits (max_jobs=1)

## Adding Worker Tasks

### 1. Create Task Functions
Tasks are pure async functions in `app/components/worker/tasks/`:
```python
# app/components/worker/tasks/my_tasks.py
async def my_background_task() -> dict[str, str]:
    """My custom background task."""
    logger.info("Running my background task")

    # Your task logic here
    await asyncio.sleep(1)  # Simulate work

    return {
        "status": "completed",
        "timestamp": datetime.now(UTC).isoformat(),
        "task": "my_background_task"
    }
```

### 2. Register with Worker Queue
Import and add to the appropriate `WorkerSettings`:
```python
# app/components/worker/queues/rod.py
from app.components.worker.tasks.my_tasks import my_background_task

class WorkerSettings:
    functions = [
        system_health_check,
        cleanup_temp_files,
        rod_sim_task,
        my_background_task,  # Add your task here
    ]

    # Standard arq configuration
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    queue_name = "arq:queue:inanimate_rod"
    max_jobs = 15
    job_timeout = 300
```

## Native arq CLI Usage

### Worker Health Checks
```bash
# Check if workers can connect to Redis and validate configuration
uv run python -m arq app.components.worker.queues.inanimate_rod.WorkerSettings --check
uv run python -m arq app.components.worker.queues.homer.WorkerSettings --check
uv run python -m arq app.components.worker.queues.lenny.WorkerSettings --check
uv run python -m arq app.components.worker.queues.carl.WorkerSettings --check
uv run python -m arq app.components.worker.queues.charlie.WorkerSettings --check
uv run python -m arq app.components.worker.queues.grimey.WorkerSettings --check
```

### Local Worker Development
```bash
# Run worker locally with auto-reload for development
uv run python -m arq app.components.worker.queues.inanimate_rod.WorkerSettings --watch app/

# Run worker in burst mode (process all jobs and exit)
uv run python -m arq app.components.worker.queues.inanimate_rod.WorkerSettings --burst
```

## Key Differences from Custom Worker Systems

### What We Do (Pure arq):
- Use native arq CLI: `python -m arq WorkerSettings`
- Standard `WorkerSettings` classes with `functions` list
- Direct task imports into worker configurations
- Native arq health checking and monitoring

### What We Don't Do (Avoided custom patterns):
- Custom worker wrapper classes
- Central worker registry systems
- Custom CLI commands for workers
- Configuration-driven task discovery

This approach keeps workers transparent and lets developers use arq exactly as documented in the official arq documentation.

## Docker Worker Debugging Commands

### View Worker Logs
```bash
# View specific worker logs
docker compose logs worker-inanimate-rod
docker compose logs worker-homer
docker compose logs worker-lenny
docker compose logs worker-carl
docker compose logs worker-charlie
docker compose logs worker-grimey

# Follow workers in real-time
docker compose logs -f worker-homer

# View all workers at once
docker compose logs -f worker-inanimate-rod worker-homer worker-lenny worker-carl worker-charlie worker-grimey

# Filter for errors
docker compose logs worker-homer | grep "ERROR\|failed\|TypeError"

# Monitor resource usage
docker stats worker-inanimate-rod worker-homer worker-lenny worker-carl worker-charlie worker-grimey
docker compose restart worker-homer
```

### Essential Docker Log Monitoring

```bash
# View real-time worker logs
docker compose logs -f worker-homer worker-lenny worker-carl

# View logs with timestamps
docker compose logs --timestamps worker-homer

# Search logs for specific errors
docker compose logs worker-homer | grep "TypeError\|failed"

# Check all service logs
docker compose logs -f
```

**System Health Verification:**
```bash
# Check all containers
docker compose ps

# Check system health via API
uv run sector-7g health status --detailed

# Monitor Redis connection
docker compose logs redis
```

## Worker Development Best Practices

### Task Design Patterns
1. **Pure Functions** - Tasks should be self-contained with minimal dependencies
2. **Error Handling** - Always include try/catch with proper logging
3. **Return Values** - Return structured data for monitoring and debugging
4. **Timeouts** - Set appropriate timeouts for different task types
5. **Retry Logic** - Use arq's built-in retry mechanisms

### Queue Management
1. **Separate Concerns** - Use different queues for different types of work
2. **Concurrency Limits** - Set appropriate max_jobs for each queue type
3. **Priority Queues** - Use different queues for different priorities
4. **Dead Letter Queues** - Monitor failed jobs and implement recovery

### Monitoring and Observability
1. **Structured Logging** - Use structured logs for easy parsing
2. **Metrics Collection** - Track task execution times and success rates
3. **Health Checks** - Implement health checks for worker availability
4. **Alerting** - Set up alerts for queue depth and failure rates

This approach ensures workers are maintainable, debuggable, and follow established patterns.

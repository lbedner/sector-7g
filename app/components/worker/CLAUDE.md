# Worker Component Development Guide

How this plant's worker is built. The backend is **taskiq** on Redis streams.

## Queues

One module per character in `app/components/worker/queues/`, each started as
its own container (`worker-homer`, `worker-lenny`, ...):

- `homer.py`, `lenny.py`, `carl.py`, `charlie.py`, `inanimate_rod.py` - the
  simulated workers.
- `grimey.py` - Frank Grimes: his simulation, plus the stack's own work
  (scheduled service jobs, backups, maintenance). There is no `system` or
  `load_test` queue here; `QueueName.SYSTEM` is `QueueName.GRIMEY`.

Every queue module has the same three parts, and the registry finds a queue
only by its module-level `broker`:

```python
from app.components.worker.broker import bind, stream_broker
from app.components.worker.tasks.lenny_tasks import file_report_task
from app.core.constants import QueueName

DESCRIPTION = "Lenny Leonard, Technical Supervisor"   # shown in the Overseer

broker = stream_broker(QueueName.LENNY)               # never build one by hand

globals().update(bind(broker, file_report_task))      # its tasks, by name
```

`stream_broker` is the one place a broker is built; `bind` registers each
function under its own name. The broker gives a job with no `timeout` of
its own its queue's (`QueueTimeout`).

## Adding a task

1. Write a plain async function in `app/components/worker/tasks/` (no
   context argument: taskiq passes only what was enqueued).
2. Add it to the `bind(...)` call of the queue that should run it.
3. Enqueue it with `await pools.enqueue_task("my_task", QueueName.LENNY)`
   (`app/components/worker/pools.py`): the one way work reaches a queue, so
   it lands in the Overseer's feed and history.

`tests/components/test_plant_queues.py` fails if Springfield enqueues a name
no queue registers.

## Adding a queue

Add its name to `QueueName` (`app/core/constants.py`), its concurrency and
timeout to `_STACK_QUEUES` (`app/core/queue_workers.py`), its module here,
and a `worker-<name>` service in `docker-compose.yml` and
`docker-compose.dev.yml`.

## Running one

```bash
docker compose exec worker-grimey /bin/bash
uv run taskiq worker app.components.worker.queues.grimey:broker --workers 1
```

## Concurrency and timeouts

How many jobs one worker process runs at once is a per-queue setting in
`app/core/config.py`, validated by the `QueueWorker` model in
`app/core/queue_workers.py`:

```python
WORKER_QUEUES: dict[str, QueueWorker]   # {"lenny": QueueWorker(concurrency=50), ...}
WORKER_QUEUE_DEFAULT: QueueWorker       # any queue not listed
```

Override from the environment as JSON:

```bash
WORKER_QUEUES='{"lenny": {"concurrency": 100}}'
```

The entrypoint passes it to taskiq as `--max-async-tasks`. A name in `WORKER_QUEUES` that matches no
queue stops the worker at startup. Each worker reports what it actually
runs with to Redis, and the Overseer's Worker > Runtime section shows it,
flagging any worker running off its setting.

## Docker Worker Debugging Commands

### View Worker Logs
```bash
# View specific worker logs
docker compose logs worker-grimey             # System worker logs
docker compose logs -f worker-grimey          # Follow system worker in real-time

# View all workers at once
docker compose logs -f worker-grimey worker-lenny

# Monitor worker processes and resources
docker compose exec worker-grimey ps aux      # Check system worker processes
docker stats worker-grimey worker-lenny   # Monitor resource usage
docker compose restart worker-grimey          # Restart specific worker
```

**Common Error Patterns:**
- `TypeError: function() got an unexpected keyword argument 'param'` - Parameter mismatch between orchestrator and task function
- `Redis connection failed` - Infrastructure connectivity problems

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
4. **Timeouts** - A task takes its queue's `timeout_seconds` (`_STACK_QUEUES`, `app/core/queue_workers.py`)
5. **Retries** - Nothing is retried: a failed job stays failed. A job cut off by a worker restart is redelivered
6. **CPU Work Off The Loop** - Run CPU-bound work through `cpu_bound` (`app.core.concurrency`): a task that computes without awaiting holds the worker's event loop, and its claim keep-alive and heartbeat with it. A queue that is mostly CPU work wants concurrency near its process count

### Queue Management
1. **Separate Concerns** - Use different queues for different types of work
2. **Concurrency Limits** - Set each queue's concurrency in `WORKER_QUEUES`
3. **Priority Queues** - Use different queues for different priorities
4. **Dead Letter Queues** - Monitor failed jobs and implement recovery

### Monitoring and Observability
1. **Structured Logging** - Use structured logs for easy parsing
2. **Metrics Collection** - Track task execution times and success rates
3. **Health Checks** - Implement health checks for worker availability
4. **Alerting** - Set up alerts for queue depth and failure rates

This approach ensures workers are maintainable, debuggable, and follow established patterns.
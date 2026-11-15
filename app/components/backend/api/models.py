"""
API models for background tasks and scheduled tasks and responses.

This module contains all Pydantic models used by the API layer for
task management, status tracking, and response formatting.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.constants import QueueName
from app.services.scheduler.models import ScheduledTask, TaskStatistics


class TaskRequest(BaseModel):
    """Request model for enqueueing a background task."""

    task_name: str = Field(..., description="Name of the task function to execute")
    queue_type: str = Field(
        QueueName.SYSTEM, description="The queue to send the task to"
    )
    args: list[Any] = Field(
        default_factory=list, description="Positional arguments for the task"
    )
    task_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="Keyword arguments for the task"
    )
    delay_seconds: int | None = Field(
        None, description="Delay task execution by this many seconds"
    )


class TaskResponse(BaseModel):
    """Response model for task enqueue operations."""

    task_id: str
    task_name: str
    queue_type: str
    queued_at: datetime
    estimated_start: datetime | None = None
    message: str


class TaskListResponse(BaseModel):
    """Response model for listing available tasks."""

    available_tasks: list[str]
    total_count: int
    queues: dict[str, list[str]]


class TaskStatusResponse(BaseModel):
    """Response model for task status checks."""

    task_id: str
    status: str = Field(
        ...,
        description="Task status: queued, in_progress, complete, failed, unknown",
    )
    enqueue_time: datetime | None = Field(
        None, description="When the task was enqueued"
    )
    start_time: datetime | None = Field(
        None, description="When the task started processing"
    )
    finish_time: datetime | None = Field(None, description="When the task completed")
    result_available: bool = Field(
        False, description="Whether task result is available"
    )
    error: str | None = Field(None, description="Error message if task failed")


class TaskResultResponse(BaseModel):
    """Response model for completed task results."""

    task_id: str
    status: str = Field(..., description="Task completion status")
    result: Any = Field(..., description="The actual task result data")
    enqueue_time: datetime | None = Field(
        None, description="When the task was enqueued"
    )
    start_time: datetime | None = Field(
        None, description="When the task started processing"
    )
    finish_time: datetime | None = Field(None, description="When the task completed")


class TaskHistoryRecord(BaseModel):
    """A single task history record from Redis."""

    job_id: str = Field(..., description="Unique task identifier")
    name: str = Field("", description="Task function name")
    queue: str = Field("", description="Queue the task was sent to")
    status: str = Field(
        "unknown", description="Task status: enqueued, running, completed, failed"
    )
    enqueued_at: str | None = Field(None, description="ISO timestamp when enqueued")
    started_at: str | None = Field(None, description="ISO timestamp when started")
    finished_at: str | None = Field(None, description="ISO timestamp when finished")
    duration_ms: str | None = Field(None, description="Duration in milliseconds")
    description: str | None = Field(None, description="Task function docstring")
    error: str | None = Field(None, description="Error message if task failed")


class TaskHistoryListResponse(BaseModel):
    """Paginated list of task history records."""

    tasks: list[TaskHistoryRecord] = Field(..., description="Task records")
    total: int = Field(..., description="Total number of records for this queue")
    offset: int = Field(0, description="Current offset")
    limit: int = Field(50, description="Page size")
    queue: str = Field(..., description="Queue name filter")


# ============================================================================
# SCHEDULED TASK API MODELS
# ============================================================================


class ScheduledTaskListResponse(BaseModel):
    """Response model for listing scheduled tasks."""

    tasks: list[ScheduledTask] = Field(..., description="List of scheduled tasks")
    total_count: int = Field(..., description="Total number of scheduled tasks")


class ScheduledTaskDetailResponse(BaseModel):
    """Response model for scheduled task details."""

    task: ScheduledTask = Field(..., description="Detailed scheduled task information")


class ScheduledTaskStatisticsResponse(BaseModel):
    """Response model for scheduled task statistics."""

    statistics: TaskStatistics = Field(..., description="Task statistics summary")


class JobExecutionRead(BaseModel):
    """A single scheduled-job run for the history list.

    ``traceback`` is intentionally omitted here to keep list payloads small;
    ``error_message`` carries the short failure reason.
    """

    id: int
    job_id: str
    job_name: str
    scheduled_run_time: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: float | None = None
    status: str
    error_message: str | None = None


class ScheduledExecutionListResponse(BaseModel):
    """Response model for paginated job execution history."""

    executions: list[JobExecutionRead] = Field(
        ..., description="Job execution records, newest first"
    )
    total: int = Field(..., description="Total executions matching the filters")


class JobRunSummary(BaseModel):
    """Compact summary of a single run (used for ``last_run``)."""

    status: str
    started_at: datetime | None = None
    duration_ms: float | None = None


class JobExecutionStatsResponse(BaseModel):
    """Aggregate execution stats for one scheduled job."""

    total_runs: int = Field(..., description="Total recorded runs")
    success_count: int = Field(..., description="Successful runs")
    failure_count: int = Field(..., description="Failed runs")
    success_rate: float = Field(..., description="Success percentage (0-100)")
    avg_duration_ms: float | None = Field(
        None, description="Average run duration in ms"
    )
    last_run: JobRunSummary | None = Field(None, description="Most recent run")


class TriggerJobResponse(BaseModel):
    """Response for a manual job trigger (Run Now)."""

    job_id: str = Field(..., description="The triggered job id")
    status: str = Field("triggered", description="Trigger outcome")
    message: str = Field(..., description="Human-readable status")
    ran_in: Literal["worker", "webserver"] = Field(
        ..., description="Where the job itself runs"
    )

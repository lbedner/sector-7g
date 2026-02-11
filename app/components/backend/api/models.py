"""
API models for background tasks and scheduled tasks and responses.

This module contains all Pydantic models used by the API layer for
task management, status tracking, and response formatting.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.services.scheduler.models import ScheduledTask, TaskStatistics


class TaskRequest(BaseModel):
    """Request model for enqueueing a background task."""

    task_name: str = Field(..., description="Name of the task function to execute")
    queue_type: str = Field(
        "system", description="Functional queue type: media or system"
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

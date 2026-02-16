"""
Charlie worker tasks for arq.

Thin wrappers around services/springfield/charlie.py functions.
"""

from typing import Any

from app.services.springfield.charlie import (
    check_emergency_exits,
    log_shift_notes,
    monitor_gauges,
    restock_break_room,
)


async def monitor_gauges_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Charlie monitors control room gauges."""
    return await monitor_gauges()


async def restock_break_room_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Charlie restocks the break room."""
    return await restock_break_room()


async def log_shift_notes_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Charlie logs shift notes."""
    return await log_shift_notes()


async def check_emergency_exits_task(
    ctx: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Charlie checks emergency exits."""
    return await check_emergency_exits()

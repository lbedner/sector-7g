"""
Carl Carlson worker tasks for arq.

Thin wrappers around services/springfield/carl.py and burns.py functions.
"""

from typing import Any

from app.services.springfield.burns import make_announcement, morning_briefing
from app.services.springfield.carl import (
    file_afternoon_reports,
    handle_inspector,
    shift_handoff,
)


async def handle_inspector_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Carl handles the NRC inspector."""
    return await handle_inspector()


async def file_afternoon_reports_task(
    ctx: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Carl files afternoon reports."""
    return await file_afternoon_reports()


async def shift_handoff_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Carl does shift handoff."""
    return await shift_handoff()


async def make_announcement_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Burns makes a plant-wide announcement (dispatched to Carl's queue)."""
    return await make_announcement()


async def morning_briefing_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Smithers preps Burns' morning briefing (dispatched to Carl's queue)."""
    return await morning_briefing()

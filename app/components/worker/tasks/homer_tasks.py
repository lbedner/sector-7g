"""
Homer Simpson worker tasks for arq.

Thin wrappers around services/springfield/homer.py functions.
"""

from typing import Any

from app.services.springfield.homer import (
    attempt_safety_check,
    clock_in,
    eat_donut,
    go_to_moes,
    nap_at_console,
    rush_out,
)


async def eat_donut_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Homer eats a donut."""
    return await eat_donut()


async def nap_at_console_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Homer naps at his console."""
    return await nap_at_console()


async def attempt_safety_check_task(
    ctx: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Homer attempts a safety check."""
    return await attempt_safety_check()


async def clock_in_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Homer clocks in (late)."""
    return await clock_in()


async def go_to_moes_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Homer goes to Moe's for lunch."""
    return await go_to_moes()


async def rush_out_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Homer rushes out at 5pm sharp."""
    return await rush_out()

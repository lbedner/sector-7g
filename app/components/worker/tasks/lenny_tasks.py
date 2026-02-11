"""
Lenny Leonard worker tasks for arq.

Thin wrappers around services/springfield/lenny.py, burns.py, and plant.py functions.
"""

from typing import Any

from app.services.springfield.burns import open_plant
from app.services.springfield.lenny import (
    check_cooling_tower,
    file_report,
    morning_inspection,
    run_diagnostics,
)
from app.services.springfield.plant import night_maintenance


async def run_diagnostics_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Lenny runs reactor diagnostics."""
    return await run_diagnostics()


async def file_report_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Lenny files a report."""
    return await file_report()


async def check_cooling_tower_task(
    ctx: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Lenny checks cooling tower sensors."""
    return await check_cooling_tower()


async def morning_inspection_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Lenny does morning inspection."""
    return await morning_inspection()


async def open_plant_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Mr. Burns opens the plant (dispatched to Lenny's queue)."""
    return await open_plant()


async def night_maintenance_task(ctx: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Automated night maintenance."""
    return await night_maintenance()

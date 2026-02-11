"""
Simulation task wrappers for Homer, Lenny, Carl, and Charlie.

Thin wrappers that pick a random activity and call the simulation service function.
"""

import random
from typing import Any

from app.services.springfield.carl import CARL_SIM_ACTIVITIES, carl_simulation
from app.services.springfield.charlie import CHARLIE_SIM_ACTIVITIES, charlie_simulation
from app.services.springfield.homer import HOMER_SIM_ACTIVITIES, homer_simulation
from app.services.springfield.lenny import LENNY_SIM_ACTIVITIES, lenny_simulation


async def homer_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Homer simulation — random activity, slow, 10% failure rate."""
    if activity is None:
        activity = random.choice(HOMER_SIM_ACTIVITIES)
    return await homer_simulation(activity)


async def lenny_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Lenny simulation — random activity, fast, 2% failure rate."""
    if activity is None:
        activity = random.choice(LENNY_SIM_ACTIVITIES)
    return await lenny_simulation(activity)


async def carl_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Carl simulation — random activity, fast, 1% failure rate."""
    if activity is None:
        activity = random.choice(CARL_SIM_ACTIVITIES)
    return await carl_simulation(activity)


async def charlie_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Charlie simulation — random activity, moderate speed, 3% failure rate."""
    if activity is None:
        activity = random.choice(CHARLIE_SIM_ACTIVITIES)
    return await charlie_simulation(activity)

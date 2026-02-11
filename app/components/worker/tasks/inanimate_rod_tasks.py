"""
Inanimate Carbon Rod worker tasks for arq.

Thin wrapper around services/springfield/inanimate_rod.py simulation function.
"""

import random
from typing import Any

from app.services.springfield.inanimate_rod import (
    ROD_SIM_ACTIVITIES,
    rod_simulation,
)


async def inanimate_rod_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Inanimate Rod simulation — random activity, steady, 1% failure rate."""
    if activity is None:
        activity = random.choice(ROD_SIM_ACTIVITIES)
    return await rod_simulation(activity)

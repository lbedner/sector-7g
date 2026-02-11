"""
Frank Grimes (deceased) worker tasks for arq.

Thin wrapper around services/springfield/grimey.py simulation function.
"""

import random
from typing import Any

from app.services.springfield.grimey import GRIMEY_SIM_ACTIVITIES, grimey_simulation


async def grimey_sim_task(
    ctx: dict[str, Any], activity: str | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Grimey simulation — random activity, meticulous, 0% failure rate."""
    if activity is None:
        activity = random.choice(GRIMEY_SIM_ACTIVITIES)
    return await grimey_simulation(activity)

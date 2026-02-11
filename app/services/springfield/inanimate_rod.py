"""
Inanimate Carbon Rod — Employee of the Month.

System maintenance tasks plus simulation. Reliable, never complains.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger

# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

ROD_SIM_ACTIVITIES = [
    "Maintain structural integrity",
    "Win Employee of the Month (again)",
    "Outperform entire Sector 7G staff",
    "Hold door open during emergency",
    "Prop up sagging ceiling tile",
    "Provide moral support to control rods",
    "Sit perfectly still in display case",
    "Reflect fluorescent lighting heroically",
    "Accept congratulations from Mr. Burns",
    "Appear on cover of Springfield Shopper",
    "Stabilize wobbling reactor housing",
    "Serve as impromptu antenna",
    "Wedge emergency hatch shut",
    "Support motivational poster on wall",
    "Exist with quiet dignity",
    "Demonstrate superior work ethic by doing nothing",
    "Be more productive than Homer",
    "Receive fan mail from NASA",
    "Maintain perfect attendance record",
    "Polish Employee of the Month plaque",
]


async def rod_simulation(activity: str) -> dict[str, Any]:
    """The Rod performs a simulation activity. Steady, 1% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Rod (sim): {activity}")

    await asyncio.sleep(random.uniform(0.5, 2.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 1% failure rate — the Rod is very reliable
    if random.random() < 0.01:
        raise RuntimeError(f"In Rod we trust, but: {activity}")

    return {
        "task": "rod_simulation",
        "character": "inanimate_rod",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

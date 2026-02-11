"""
Frank Grimes (deceased) — Employee #4763.

Meticulous, thorough, zero failure rate. Works from beyond the grave.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger

# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

GRIMEY_SIM_ACTIVITIES = [
    "Audit Homer's safety inspection records (posthumously)",
    "File OSHA complaint from beyond the grave",
    "Grade Homer's safety exam (score: -4)",
    "Document every code violation in Sector 7G",
    "Write strongly-worded memo about donut crumbs on control panel",
    "Calculate exact cost of Homer's incompetence to taxpayers",
    "Compile evidence for Homer's termination (volume 47)",
    "Review plant's liability insurance (insufficient)",
    "Cross-reference Homer's attendance with Moe's Tavern hours",
    "Draft proposal for minimum competency requirements",
    "Alphabetize Homer's incident reports (needs second filing cabinet)",
    "Verify Homer's claimed qualifications (found none)",
    "Calculate radiation exposure from Homer's 'experiments'",
    "Compose letter to Nuclear Regulatory Commission",
    "Inventory every safety violation visible from Sector 7G",
    "Fact-check Homer's resume (88% fabricated)",
    "Prepare presentation: 'Why Homer Should Not Work Here'",
    "Document structural damage from Homer's bowling practice",
    "Catalog items Homer has broken this quarter (437 items)",
    "Write performance review for Homer (unprintable)",
]


async def grimey_simulation(activity: str) -> dict[str, Any]:
    """Grimey performs a simulation activity. Meticulous, 0% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Grimey (sim): {activity}")

    # Grimey is thorough — he takes his time
    await asyncio.sleep(random.uniform(10.0, 20.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 0% failure rate — Frank Grimes does NOT fail
    return {
        "task": "grimey_simulation",
        "character": "grimey",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

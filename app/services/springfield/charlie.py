"""
Charlie — Plant Worker, Springfield Nuclear Power Plant.

I/O-bound, moderate-speed tasks. Charlie just shows up and does the work.
Not flashy, not lazy — just a regular guy at a nuclear plant.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger


async def monitor_gauges() -> dict[str, Any]:
    """Charlie monitors the control room gauges. Routine but attentive."""
    start = datetime.now(UTC)
    logger.info("Charlie: Checking the gauges...")

    gauges = []
    for gauge in ["pressure", "temperature", "flow_rate", "coolant_level"]:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        gauges.append({
            "gauge": gauge,
            "reading": round(random.uniform(90, 100), 1),
            "status": "normal",
        })

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "monitor_gauges",
        "character": "charlie",
        "status": "completed",
        "message": "All gauges in normal range. Charlie's on it.",
        "gauges_checked": len(gauges),
        "duration_ms": round(duration_ms, 2),
    }


async def restock_break_room() -> dict[str, Any]:
    """Charlie restocks the break room. Someone has to do it."""
    start = datetime.now(UTC)
    logger.info("Charlie: Restocking the break room...")

    items = ["coffee", "donuts", "paper towels", "creamer", "sugar"]
    restocked = []
    for item in items:
        await asyncio.sleep(random.uniform(0.05, 0.1))
        restocked.append(item)

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "restock_break_room",
        "character": "charlie",
        "status": "completed",
        "message": f"Break room restocked. {len(restocked)} items replenished.",
        "items_restocked": restocked,
        "homer_already_ate_donuts": random.random() < 0.7,
        "duration_ms": round(duration_ms, 2),
    }


async def log_shift_notes() -> dict[str, Any]:
    """Charlie logs shift notes. Diligent record-keeping."""
    start = datetime.now(UTC)
    logger.info("Charlie: Writing up shift notes...")

    await asyncio.sleep(random.uniform(0.1, 0.3))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "log_shift_notes",
        "character": "charlie",
        "status": "completed",
        "message": "Shift notes logged. Nothing unusual (besides Homer).",
        "pages_written": random.randint(1, 3),
        "homer_incidents_noted": random.randint(0, 4),
        "duration_ms": round(duration_ms, 2),
    }


async def check_emergency_exits() -> dict[str, Any]:
    """Charlie checks emergency exits. Safety first."""
    start = datetime.now(UTC)
    logger.info("Charlie: Checking emergency exits...")

    exits = []
    for exit_id in range(1, 7):
        await asyncio.sleep(random.uniform(0.03, 0.08))
        blocked = exit_id == 3 and random.random() < 0.3
        exits.append({
            "exit": f"E-{exit_id}",
            "clear": not blocked,
            "blocked_by": "Homer's car" if blocked else None,
        })

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    all_clear = all(e["clear"] for e in exits)
    return {
        "task": "check_emergency_exits",
        "character": "charlie",
        "status": "completed",
        "message": (
            "All exits clear."
            if all_clear
            else "Exit E-3 blocked by Homer's car. Again."
        ),
        "exits_checked": len(exits),
        "all_clear": all_clear,
        "duration_ms": round(duration_ms, 2),
    }


# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

CHARLIE_SIM_ACTIVITIES = [
    "Refill coffee pot in break room",
    "Replace burnt-out hallway light",
    "Sweep up donut crumbs from Sector 7G",
    "Fix paper jam in copy machine",
    "Water the office plants",
    "Tape up motivational poster Homer ripped",
    "Unclog break room sink",
    "Sort incoming mail for the floor",
    "Update safety board tally (days without incident: 0)",
    "Move Homer's car out of fire lane",
    "Report pothole in parking lot B",
    "Wipe down control room consoles",
    "Reset tripped circuit breaker in hallway",
    "Collect Homer's forgotten lunch box",
    "Adjust thermostat (someone set it to 85)",
    "Organize supply closet",
    "Replace first aid kit supplies",
    "Fix squeaky door on reactor floor",
    "Take out the recycling",
    "Clean up coffee spill in control room",
]


async def charlie_simulation(activity: str) -> dict[str, Any]:
    """Charlie performs a simulation activity. Moderate speed, 3% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Charlie (sim): {activity}")

    # Charlie works at a steady, reliable pace
    await asyncio.sleep(random.uniform(0.5, 2.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 3% failure rate — Charlie is reliable but things happen
    if random.random() < 0.03:
        raise RuntimeError(f"Charlie ran into trouble: {activity}")

    return {
        "task": "charlie_simulation",
        "character": "charlie",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

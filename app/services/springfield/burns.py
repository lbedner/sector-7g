"""
Charles Montgomery Burns — Plant Owner.

Admin/announcement functions. Quick tasks dispatched to other queues.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger


async def open_plant() -> dict[str, Any]:
    """Mr. Burns opens the plant for the day. Excellent..."""
    start = datetime.now(UTC)
    logger.info("Burns: Excellent...")

    await asyncio.sleep(random.uniform(0.2, 0.5))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "open_plant",
        "character": "burns",
        "status": "completed",
        "message": "Excellent... The plant is now operational.",
        "mood": random.choice(["excellent", "diabolical", "scheming"]),
        "hounds_released": False,
        "duration_ms": round(duration_ms, 2),
    }


async def make_announcement() -> dict[str, Any]:
    """Mr. Burns makes a plant-wide announcement."""
    start = datetime.now(UTC)
    logger.info("Burns: Attention all employees...")

    await asyncio.sleep(random.uniform(0.1, 0.3))

    announcement = random.choice(
        [
            "Attention: The beatings will continue until morale improves.",
            "Reminder: Employee of the Month parking has been converted to my helipad.",
            "The vending machines now accept company scrip only.",
            "All employees must work through the weekend. Excellent.",
            "I've decided to block out the sun. Details to follow.",
        ]
    )

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "make_announcement",
        "character": "burns",
        "status": "completed",
        "message": announcement,
        "employee_morale_impact": random.choice(
            ["decreased", "significantly decreased"]
        ),
        "duration_ms": round(duration_ms, 2),
    }


async def morning_briefing() -> dict[str, Any]:
    """Smithers preps Burns' morning briefing."""
    start = datetime.now(UTC)
    logger.info("Smithers: Preparing Mr. Burns' morning briefing...")

    # Smithers gathers reports
    async def gather_report(dept: str) -> dict[str, str]:
        await asyncio.sleep(random.uniform(0.05, 0.1))
        return {"department": dept, "status": "reported"}

    depts = ["operations", "safety", "finance", "legal"]
    reports = await asyncio.gather(*[gather_report(d) for d in depts])

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "morning_briefing",
        "character": "smithers",
        "status": "completed",
        "message": (
            "Smithers has prepared Mr. Burns' morning briefing."
            " All departments reported."
        ),
        "departments_reporting": len(reports),
        "burns_attention_span": random.choice(
            ["minimal", "nonexistent", "distracted by hounds"]
        ),
        "duration_ms": round(duration_ms, 2),
    }

"""
Homer Simpson — Safety Inspector, Sector 7G.

CPU-bound, slow tasks. The whole point is that Homer's queue backs up.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger


async def eat_donut() -> dict[str, Any]:
    """Homer eats a donut. Fibonacci + sleep. Mmm... donuts."""
    start = datetime.now(UTC)
    logger.info("Homer: Mmm... donuts...")

    # CPU work: fibonacci
    n = random.randint(800, 1200)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    # Homer savors every bite
    await asyncio.sleep(random.uniform(2.0, 5.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "eat_donut",
        "character": "homer",
        "status": "completed",
        "message": "Mmm... donuts...",
        "donut_type": random.choice([
            "pink sprinkled", "chocolate glazed", "jelly filled",
            "maple bar", "cruller", "boston cream",
        ]),
        "fibonacci_n": n,
        "duration_ms": round(duration_ms, 2),
    }


async def nap_at_console() -> dict[str, Any]:
    """Homer naps at his console in Sector 7G. Long sleep."""
    start = datetime.now(UTC)
    logger.info("Homer: *snoring at console*")

    await asyncio.sleep(random.uniform(3.0, 8.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    snore_sounds = random.choice(["Zzzzz...", "Hrrrnk... zzz...", "*drool*"])
    return {
        "task": "nap_at_console",
        "character": "homer",
        "status": "completed",
        "message": f"Homer napping at Sector 7G console. {snore_sounds}",
        "warning_lights_ignored": random.randint(1, 12),
        "duration_ms": round(duration_ms, 2),
    }


async def attempt_safety_check() -> dict[str, Any]:
    """Homer attempts a safety check. 30% chance he actually does it."""
    start = datetime.now(UTC)
    logger.info("Homer: Safety check? D'oh!")

    # Matrix multiplication — Homer struggles with the clipboard
    size = random.randint(30, 60)
    matrix_a = [[random.random() for _ in range(size)] for _ in range(size)]
    matrix_b = [[random.random() for _ in range(size)] for _ in range(size)]
    result = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    await asyncio.sleep(random.uniform(2.0, 5.0))

    passed = random.random() < 0.3  # 30% chance of "passing"
    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    if passed:
        message = "Homer somehow passed the safety check. Mr. Burns is suspicious."
    else:
        message = "Homer checked 'all clear' without looking. Classic Homer."

    return {
        "task": "attempt_safety_check",
        "character": "homer",
        "status": "completed",
        "passed": passed,
        "message": message,
        "items_actually_checked": 0 if not passed else random.randint(1, 3),
        "matrix_size": size,
        "duration_ms": round(duration_ms, 2),
    }


async def clock_in() -> dict[str, Any]:
    """Homer clocks in. He's late and can't find his badge."""
    start = datetime.now(UTC)
    logger.info("Homer: Where's my badge? D'oh!")

    # CPU work: searching for badge (sorting through junk)
    junk = [random.randint(1, 10000) for _ in range(5000)]
    sorted(junk)

    await asyncio.sleep(random.uniform(2.0, 4.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "clock_in",
        "character": "homer",
        "status": "completed",
        "message": "Homer clocked in. Only 15 minutes late (personal best).",
        "minutes_late": random.randint(10, 45),
        "badge_found_in": random.choice([
            "car seat", "donut box", "pants pocket",
            "Bart's backpack", "under the couch",
        ]),
        "duration_ms": round(duration_ms, 2),
    }


async def go_to_moes() -> dict[str, Any]:
    """Homer goes to Moe's for lunch. Extended break."""
    start = datetime.now(UTC)
    logger.info("Homer: Moe's Tavern, here I come!")

    await asyncio.sleep(random.uniform(5.0, 10.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "go_to_moes",
        "character": "homer",
        "status": "completed",
        "message": "Homer returned from Moe's. Smells like Duff.",
        "duffs_consumed": random.randint(2, 6),
        "bar_tab": round(random.uniform(8.50, 24.00), 2),
        "duration_ms": round(duration_ms, 2),
    }


async def rush_out() -> dict[str, Any]:
    """Homer rushes out at 5pm sharp. Minimal work — he's efficient at leaving."""
    start = datetime.now(UTC)
    logger.info("Homer: Woohoo! Quitting time!")

    # Minimal work — Homer is VERY efficient at leaving
    await asyncio.sleep(random.uniform(0.1, 0.5))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "rush_out",
        "character": "homer",
        "status": "completed",
        "message": "Homer left the building in record time. Tire marks in parking lot.",
        "exit_speed": "maximum",
        "items_left_behind": random.choice([
            "lunch box", "hard hat", "dignity", "safety manual",
        ]),
        "duration_ms": round(duration_ms, 2),
    }


# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

HOMER_SIM_ACTIVITIES = [
    "Press random buttons on console",
    "Read donut catalog instead of safety manual",
    "Google 'is plutonium spicy'",
    "Hide Duff beer in filing cabinet",
    "Practice bowling swing in control room",
    "Call Marge to complain about work",
    "Doodle on reactor schematics",
    "Microwave fish in the break room",
    "Try to remember nuclear safety protocol",
    "Argue with vending machine",
    "Fall asleep during safety briefing",
    "Photocopy face on office copier",
    "Build donut tower on control panel",
    "Watch Itchy & Scratchy on work computer",
    "Accidentally vent steam from cooling tower",
    "Blame Lenny for missing paperwork",
    "Eat lunch at 9:30 AM",
    "Lock keys inside reactor containment",
    "Use safety checklist as napkin",
    "Ask Smithers what all the blinking lights mean",
]


async def homer_simulation(activity: str) -> dict[str, Any]:
    """Homer performs a simulation activity. Slow, 25% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Homer (sim): {activity}")

    # Homer is slow — naps, daydreams, stares at the blinking lights
    await asyncio.sleep(random.uniform(6.0, 12.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 25% failure rate — Homer is not good at his job
    if random.random() < 0.25:
        raise RuntimeError(f"D'oh! Homer failed: {activity}")

    return {
        "task": "homer_simulation",
        "character": "homer",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

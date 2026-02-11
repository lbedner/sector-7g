"""
Lenny Leonard — Technical Supervisor.

I/O-bound, fast tasks. Lenny is competent and gets things done quickly.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger


async def run_diagnostics() -> dict[str, Any]:
    """Lenny runs reactor diagnostics. Concurrent async ops."""
    start = datetime.now(UTC)
    logger.info("Lenny: Running reactor diagnostics...")

    async def check_system(name: str) -> dict[str, Any]:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        return {
            "system": name,
            "status": "nominal",
            "reading": round(random.uniform(95, 100), 1),
        }

    systems = [
        "coolant_flow", "pressure_vessel", "control_rods",
        "steam_generator", "turbine",
    ]
    results = await asyncio.gather(*[check_system(s) for s in systems])

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "run_diagnostics",
        "character": "lenny",
        "status": "completed",
        "message": "All reactor systems nominal. Lenny's got it covered.",
        "systems_checked": len(results),
        "all_nominal": all(r["status"] == "nominal" for r in results),
        "duration_ms": round(duration_ms, 2),
    }


async def file_report() -> dict[str, Any]:
    """Lenny files a report. Quick async I/O."""
    start = datetime.now(UTC)
    logger.info("Lenny: Filing daily report...")

    await asyncio.sleep(random.uniform(0.1, 0.3))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "file_report",
        "character": "lenny",
        "status": "completed",
        "message": "Report filed. Unlike Homer, Lenny actually reads the forms.",
        "report_type": random.choice([
            "daily operations", "safety compliance", "maintenance log",
            "incident report (Homer-related)",
        ]),
        "pages": random.randint(2, 8),
        "duration_ms": round(duration_ms, 2),
    }


async def check_cooling_tower() -> dict[str, Any]:
    """Lenny checks cooling tower sensors. Concurrent reads."""
    start = datetime.now(UTC)
    logger.info("Lenny: Checking cooling tower sensors...")

    async def read_sensor(sensor_id: int) -> dict[str, Any]:
        await asyncio.sleep(random.uniform(0.02, 0.08))
        return {
            "sensor_id": sensor_id,
            "temp_celsius": round(random.uniform(35, 45), 1),
            "flow_rate": round(random.uniform(800, 1200), 0),
            "status": "normal",
        }

    sensors = await asyncio.gather(*[read_sensor(i) for i in range(8)])

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    avg_temp = round(sum(s["temp_celsius"] for s in sensors) / len(sensors), 1)
    return {
        "task": "check_cooling_tower",
        "character": "lenny",
        "status": "completed",
        "message": f"Cooling tower nominal. Avg temp: {avg_temp}°C",
        "sensors_read": len(sensors),
        "avg_temperature": avg_temp,
        "duration_ms": round(duration_ms, 2),
    }


async def morning_inspection() -> dict[str, Any]:
    """Lenny does morning inspection. Series of quick async checks."""
    start = datetime.now(UTC)
    logger.info("Lenny: Starting morning inspection...")

    checks = []
    for area in ["reactor_floor", "control_room", "turbine_hall", "waste_storage"]:
        await asyncio.sleep(random.uniform(0.05, 0.1))
        checks.append({
            "area": area,
            "status": "clear",
            "homer_spotted": area == "control_room" and random.random() < 0.5,
        })

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    homer_sighting = any(c["homer_spotted"] for c in checks)
    return {
        "task": "morning_inspection",
        "character": "lenny",
        "status": "completed",
        "message": "Morning inspection complete."
        + (" Homer spotted napping." if homer_sighting else ""),
        "areas_inspected": len(checks),
        "all_clear": True,
        "homer_sighting": homer_sighting,
        "duration_ms": round(duration_ms, 2),
    }


# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

LENNY_SIM_ACTIVITIES = [
    "Calibrate pressure gauge #47",
    "Log coolant temperature reading",
    "Update reactor output spreadsheet",
    "Review morning safety checklist",
    "Check fire extinguisher expiration dates",
    "Verify emergency exit signage",
    "Test backup generator startup sequence",
    "Inspect containment seal integrity",
    "Record turbine RPM fluctuations",
    "Swap out dosimeter badges",
    "File weekly radiation exposure report",
    "Restock first aid station",
    "Test emergency shower functionality",
    "Verify control rod insertion depth",
    "Update shift change log",
    "Check ventilation system filters",
    "Run steam pressure valve test",
    "Audit safety equipment inventory",
    "Calibrate Geiger counter #12",
    "Document Homer's latest safety violation",
]


async def lenny_simulation(activity: str) -> dict[str, Any]:
    """Lenny performs a simulation activity. Fast, 2% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Lenny (sim): {activity}")

    # Concurrent async pattern — Lenny is efficient
    async def _check() -> None:
        await asyncio.sleep(random.uniform(0.05, 0.15))

    await asyncio.gather(*[_check() for _ in range(3)])
    await asyncio.sleep(random.uniform(0.3, 1.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 2% failure rate
    if random.random() < 0.02:
        raise RuntimeError(f"Lenny hit a snag: {activity}")

    return {
        "task": "lenny_simulation",
        "character": "lenny",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

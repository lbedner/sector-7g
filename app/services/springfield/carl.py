"""
Carl Carlson — Technical Supervisor.

I/O-bound, fast tasks. Carl handles inspectors and reports efficiently.
"""

import asyncio
from datetime import UTC, datetime
import random
from typing import Any

from app.core.log import logger


async def handle_inspector() -> dict[str, Any]:
    """Carl handles the NRC inspector visit. Quick async ops."""
    start = datetime.now(UTC)
    logger.info("Carl: NRC inspector is here. I'll handle this.")

    # Prepare documentation
    async def prep_document(doc: str) -> dict[str, str]:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        return {"document": doc, "status": "prepared"}

    docs = ["safety_logs", "maintenance_records", "training_certs", "incident_reports"]
    prepared = await asyncio.gather(*[prep_document(d) for d in docs])

    # Distract from Sector 7G
    await asyncio.sleep(random.uniform(0.1, 0.2))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "handle_inspector",
        "character": "carl",
        "status": "completed",
        "message": "Inspector visit handled. Sector 7G was NOT on the tour.",
        "documents_prepared": len(prepared),
        "sector_7g_avoided": True,
        "inspector_satisfaction": random.choice(["satisfied", "mostly satisfied"]),
        "duration_ms": round(duration_ms, 2),
    }


async def file_afternoon_reports() -> dict[str, Any]:
    """Carl files afternoon reports. Quick async I/O."""
    start = datetime.now(UTC)
    logger.info("Carl: Filing afternoon reports...")

    reports = []
    for report in ["operations_summary", "safety_metrics", "personnel_log"]:
        await asyncio.sleep(random.uniform(0.05, 0.1))
        reports.append({"report": report, "filed": True})

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "file_afternoon_reports",
        "character": "carl",
        "status": "completed",
        "message": f"Filed {len(reports)} afternoon reports. All accounted for.",
        "reports_filed": len(reports),
        "homer_incident_noted": random.random() < 0.4,
        "duration_ms": round(duration_ms, 2),
    }


async def shift_handoff() -> dict[str, Any]:
    """Carl does the shift handoff checklist."""
    start = datetime.now(UTC)
    logger.info("Carl: Running shift handoff checklist...")

    checklist = [
        "reactor_status",
        "open_work_orders",
        "safety_briefing",
        "key_handoff",
        "log_review",
    ]
    completed = []
    for item in checklist:
        await asyncio.sleep(random.uniform(0.03, 0.08))
        completed.append({"item": item, "checked": True})

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000
    return {
        "task": "shift_handoff",
        "character": "carl",
        "status": "completed",
        "message": "Shift handoff complete. Night crew briefed.",
        "items_checked": len(completed),
        "all_complete": True,
        "homer_left_early": random.random() < 0.8,
        "duration_ms": round(duration_ms, 2),
    }


# =============================================================================
# SIMULATION — continuous background activity
# =============================================================================

CARL_SIM_ACTIVITIES = [
    "Update personnel attendance log",
    "Process visitor badge request",
    "File quarterly compliance report",
    "Schedule conference room for safety meeting",
    "Order replacement PPE for Sector 7G",
    "Review overtime authorization requests",
    "Update emergency contact database",
    "Process equipment maintenance request",
    "Coordinate with external auditor",
    "Review training completion records",
    "Submit budget variance report",
    "Update organizational chart (again)",
    "Process Homer's 47th incident report this month",
    "Arrange catering for Burns' birthday",
    "File workers' compensation claim (Homer)",
    "Update parking lot assignment spreadsheet",
    "Schedule annual fire drill",
    "Process new hire orientation checklist",
    "Review and approve purchase orders",
    "Reconcile petty cash (missing $4.50 — probably Homer)",
]


async def carl_simulation(activity: str) -> dict[str, Any]:
    """Carl performs a simulation activity. Fast sequential I/O, 1% failure rate."""
    start = datetime.now(UTC)
    logger.info(f"Carl (sim): {activity}")

    # Sequential brief I/O — Carl is methodical
    for _ in range(2):
        await asyncio.sleep(random.uniform(0.1, 0.3))

    await asyncio.sleep(random.uniform(0.3, 1.0))

    duration_ms = (datetime.now(UTC) - start).total_seconds() * 1000

    # 1% failure rate
    if random.random() < 0.01:
        raise RuntimeError(f"Carl encountered an issue: {activity}")

    return {
        "task": "carl_simulation",
        "character": "carl",
        "status": "completed",
        "activity": activity,
        "duration_ms": round(duration_ms, 2),
    }

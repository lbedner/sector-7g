"""Springfield Nuclear Power Plant schedule registry.

Code is the source of truth for schedules under the 0.10 template: any
persisted job whose id is not registered here gets swept as an orphan on
scheduler startup. These 26 jobs were originally added at runtime and
recovered from the production jobstore (apscheduler_jobs_backup.sql,
2026-09-02) with their exact triggers.
"""

from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.springfield import scheduler_jobs, simulation

PLANT_TZ = "America/Chicago"

# (job_id, name, func, hour, minute) - the plant's daily routine
_DAILY_ROUTINE: list[tuple[str, str, Any, int, int]] = [
    ("burns_opens_plant", "Burns Opens Plant", scheduler_jobs.burns_opens_plant, 6, 0),
    (
        "smithers_morning_briefing",
        "Smithers Morning Briefing",
        scheduler_jobs.smithers_morning_briefing,
        6,
        30,
    ),
    (
        "lenny_carl_arrive",
        "Lenny & Carl Arrive",
        scheduler_jobs.lenny_carl_arrive,
        7,
        0,
    ),
    (
        "homer_alarm_snooze",
        "Homer Alarm Snooze",
        scheduler_jobs.homer_alarm_snooze,
        7,
        45,
    ),
    (
        "homer_clocks_in",
        "Homer Clocks In (Late)",
        scheduler_jobs.homer_clocks_in,
        8,
        15,
    ),
    ("morning_donut_run", "Morning Donut Run", scheduler_jobs.morning_donut_run, 8, 30),
    (
        "sector_7g_inspection",
        "Sector 7G Inspection",
        scheduler_jobs.sector_7g_inspection,
        9,
        0,
    ),
    (
        "homer_descends_to_7g",
        "Homer Descends to 7G",
        scheduler_jobs.homer_descends_to_7g,
        9,
        45,
    ),
    (
        "health_inspector_visit",
        "NRC Inspector Visit",
        scheduler_jobs.health_inspector_visit,
        10,
        0,
    ),
    (
        "homer_nap_attempt",
        "Homer Nap Attempt",
        scheduler_jobs.homer_nap_attempt,
        10,
        30,
    ),
    (
        "burns_announcement",
        "Burns Announcement",
        scheduler_jobs.burns_announcement,
        11,
        30,
    ),
    ("lunch_at_moes", "Lunch at Moe's", scheduler_jobs.lunch_at_moes, 12, 0),
    (
        "afternoon_diagnostics",
        "Afternoon Diagnostics",
        scheduler_jobs.afternoon_diagnostics,
        13,
        0,
    ),
    (
        "homer_safety_check",
        "Homer Safety Check",
        scheduler_jobs.homer_safety_check,
        14,
        0,
    ),
    (
        "carl_files_reports",
        "Carl Files Reports",
        scheduler_jobs.carl_files_reports,
        15,
        0,
    ),
    (
        "cooling_tower_check",
        "Cooling Tower Check",
        scheduler_jobs.cooling_tower_check,
        16,
        0,
    ),
    (
        "homer_another_donut",
        "Homer Afternoon Donut",
        scheduler_jobs.homer_another_donut,
        16,
        30,
    ),
    ("end_of_shift", "End of Shift", scheduler_jobs.end_of_shift, 17, 0),
    (
        "evening_handoff",
        "Evening Shift Handoff",
        scheduler_jobs.evening_handoff,
        17,
        30,
    ),
    (
        "night_maintenance",
        "Night Maintenance",
        scheduler_jobs.night_maintenance_job,
        22,
        0,
    ),
]

# (job_id, name, func, interval_seconds) - continuous work generators
_SIMULATIONS: list[tuple[str, str, Any, int]] = [
    ("sim_homer", "Homer Simulation Work", simulation.generate_homer_work, 10),
    ("sim_lenny", "Lenny Simulation Work", simulation.generate_lenny_work, 5),
    ("sim_carl", "Carl Simulation Work", simulation.generate_carl_work, 5),
    ("sim_charlie", "Charlie Simulation Work", simulation.generate_charlie_work, 15),
    (
        "sim_inanimate_rod",
        "Inanimate Rod Simulation Work",
        simulation.generate_inanimate_rod_work,
        15,
    ),
    ("sim_grimey", "Grimey Simulation Work", simulation.generate_grimey_work, 3600),
]


def register_springfield_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register the plant's daily routine and simulation generators."""
    for job_id, name, func, hour, minute in _DAILY_ROUTINE:
        scheduler.add_job(
            func,
            trigger="cron",
            hour=hour,
            minute=minute,
            timezone=PLANT_TZ,
            id=job_id,
            name=name,
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    for job_id, name, func, seconds in _SIMULATIONS:
        scheduler.add_job(
            func,
            trigger="interval",
            seconds=seconds,
            id=job_id,
            name=name,
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )

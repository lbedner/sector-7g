"""
Springfield Nuclear Power Plant — Scheduler trigger functions.

Each function enqueues tasks into character queues via enqueue_task().
Called by APScheduler cron triggers on a daily timeline.
"""

from app.components.worker import pools
from app.core.constants import QueueName
from app.core.log import logger


async def burns_opens_plant() -> None:
    """6:00 AM — Mr. Burns arrives, plant goes online."""
    logger.info("Scheduler: Burns opens plant")
    await pools.enqueue_task("open_plant_task", QueueName.LENNY)


async def smithers_morning_briefing() -> None:
    """6:30 AM — Smithers preps Burns' morning briefing."""
    logger.info("Scheduler: Smithers morning briefing")
    await pools.enqueue_task("morning_briefing_task", QueueName.CARL)


async def lenny_carl_arrive() -> None:
    """7:00 AM — Lenny & Carl arrive, morning diagnostics."""
    logger.info("Scheduler: Lenny & Carl arrive")
    await pools.enqueue_task("morning_inspection_task", QueueName.LENNY)
    await pools.enqueue_task("run_diagnostics_task", QueueName.LENNY)


async def homer_alarm_snooze() -> None:
    """7:45 AM — Homer's alarm goes off. He snoozes."""
    logger.info("Scheduler: Homer's alarm (he snoozes)")
    await pools.enqueue_task("nap_at_console_task", QueueName.HOMER)


async def homer_clocks_in() -> None:
    """8:15 AM — Homer arrives (late, as usual)."""
    logger.info("Scheduler: Homer clocks in (late)")
    await pools.enqueue_task("clock_in_task", QueueName.HOMER)


async def morning_donut_run() -> None:
    """8:30 AM — First donut break."""
    logger.info("Scheduler: Morning donut run")
    await pools.enqueue_task("eat_donut_task", QueueName.HOMER)


async def sector_7g_inspection() -> None:
    """9:00 AM — Lenny runs safety inspection."""
    logger.info("Scheduler: Sector 7G inspection (Lenny)")
    await pools.enqueue_task("morning_inspection_task", QueueName.LENNY)
    await pools.enqueue_task("file_report_task", QueueName.LENNY)


async def homer_descends_to_7g() -> None:
    """9:45 AM — Homer goes to his station in Sector 7G."""
    logger.info("Scheduler: Homer descends to Sector 7G")
    await pools.enqueue_task("eat_donut_task", QueueName.HOMER)


async def health_inspector_visit() -> None:
    """10:00 AM — NRC inspector visit (Carl handles it)."""
    logger.info("Scheduler: NRC inspector visit")
    await pools.enqueue_task("handle_inspector_task", QueueName.CARL)


async def homer_nap_attempt() -> None:
    """10:30 AM — Homer naps at console."""
    logger.info("Scheduler: Homer nap attempt")
    await pools.enqueue_task("nap_at_console_task", QueueName.HOMER)


async def burns_announcement() -> None:
    """11:30 AM — Plant-wide announcement from Burns."""
    logger.info("Scheduler: Burns announcement")
    await pools.enqueue_task("make_announcement_task", QueueName.CARL)


async def lunch_at_moes() -> None:
    """12:00 PM — Homer goes to Moe's for lunch."""
    logger.info("Scheduler: Homer goes to Moe's")
    await pools.enqueue_task("go_to_moes_task", QueueName.HOMER)


async def afternoon_diagnostics() -> None:
    """1:00 PM — Lenny runs afternoon diagnostics."""
    logger.info("Scheduler: Afternoon diagnostics (Lenny)")
    await pools.enqueue_task("run_diagnostics_task", QueueName.LENNY)
    await pools.enqueue_task("file_report_task", QueueName.LENNY)


async def homer_safety_check() -> None:
    """2:00 PM — Homer attempts safety check."""
    logger.info("Scheduler: Homer safety check")
    await pools.enqueue_task("attempt_safety_check_task", QueueName.HOMER)


async def carl_files_reports() -> None:
    """3:00 PM — Carl files afternoon reports."""
    logger.info("Scheduler: Carl files reports")
    await pools.enqueue_task("file_afternoon_reports_task", QueueName.CARL)


async def cooling_tower_check() -> None:
    """4:00 PM — Lenny checks cooling tower."""
    logger.info("Scheduler: Cooling tower check (Lenny)")
    await pools.enqueue_task("check_cooling_tower_task", QueueName.LENNY)


async def homer_another_donut() -> None:
    """4:30 PM — Afternoon donut."""
    logger.info("Scheduler: Homer afternoon donut")
    await pools.enqueue_task("eat_donut_task", QueueName.HOMER)


async def end_of_shift() -> None:
    """5:00 PM — Homer rushes out at 5pm sharp."""
    logger.info("Scheduler: End of shift — Homer OUT")
    await pools.enqueue_task("rush_out_task", QueueName.HOMER)


async def evening_handoff() -> None:
    """5:30 PM — Lenny & Carl shift handoff."""
    logger.info("Scheduler: Evening shift handoff")
    await pools.enqueue_task("shift_handoff_task", QueueName.CARL)


async def night_maintenance_job() -> None:
    """10:00 PM — Automated night maintenance."""
    logger.info("Scheduler: Night maintenance")
    await pools.enqueue_task("night_maintenance_task", QueueName.LENNY)

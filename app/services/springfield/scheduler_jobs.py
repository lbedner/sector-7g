"""
Springfield Nuclear Power Plant — Scheduler trigger functions.

Each function enqueues tasks into character queues via get_queue_pool().
Called by APScheduler cron triggers on a daily timeline.
"""

from app.core.log import logger


async def burns_opens_plant() -> None:
    """6:00 AM — Mr. Burns arrives, plant goes online."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Burns opens plant")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("open_plant_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def smithers_morning_briefing() -> None:
    """6:30 AM — Smithers preps Burns' morning briefing."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Smithers morning briefing")
    pool, queue_name = await get_queue_pool("carl")
    try:
        await pool.enqueue_job("morning_briefing_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def lenny_carl_arrive() -> None:
    """7:00 AM — Lenny & Carl arrive, morning diagnostics."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Lenny & Carl arrive")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("morning_inspection_task", _queue_name=queue_name)
        await pool.enqueue_job("run_diagnostics_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_alarm_snooze() -> None:
    """7:45 AM — Homer's alarm goes off. He snoozes."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer's alarm (he snoozes)")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("nap_at_console_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_clocks_in() -> None:
    """8:15 AM — Homer arrives (late, as usual)."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer clocks in (late)")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("clock_in_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def morning_donut_run() -> None:
    """8:30 AM — First donut break."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Morning donut run")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("eat_donut_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def sector_7g_inspection() -> None:
    """9:00 AM — Lenny runs safety inspection."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Sector 7G inspection (Lenny)")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("morning_inspection_task", _queue_name=queue_name)
        await pool.enqueue_job("file_report_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_descends_to_7g() -> None:
    """9:45 AM — Homer goes to his station in Sector 7G."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer descends to Sector 7G")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("eat_donut_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def health_inspector_visit() -> None:
    """10:00 AM — NRC inspector visit (Carl handles it)."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: NRC inspector visit")
    pool, queue_name = await get_queue_pool("carl")
    try:
        await pool.enqueue_job("handle_inspector_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_nap_attempt() -> None:
    """10:30 AM — Homer naps at console."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer nap attempt")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("nap_at_console_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def burns_announcement() -> None:
    """11:30 AM — Plant-wide announcement from Burns."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Burns announcement")
    pool, queue_name = await get_queue_pool("carl")
    try:
        await pool.enqueue_job("make_announcement_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def lunch_at_moes() -> None:
    """12:00 PM — Homer goes to Moe's for lunch."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer goes to Moe's")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("go_to_moes_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def afternoon_diagnostics() -> None:
    """1:00 PM — Lenny runs afternoon diagnostics."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Afternoon diagnostics (Lenny)")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("run_diagnostics_task", _queue_name=queue_name)
        await pool.enqueue_job("file_report_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_safety_check() -> None:
    """2:00 PM — Homer attempts safety check."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer safety check")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("attempt_safety_check_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def carl_files_reports() -> None:
    """3:00 PM — Carl files afternoon reports."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Carl files reports")
    pool, queue_name = await get_queue_pool("carl")
    try:
        await pool.enqueue_job("file_afternoon_reports_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def cooling_tower_check() -> None:
    """4:00 PM — Lenny checks cooling tower."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Cooling tower check (Lenny)")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("check_cooling_tower_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def homer_another_donut() -> None:
    """4:30 PM — Afternoon donut."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Homer afternoon donut")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("eat_donut_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def end_of_shift() -> None:
    """5:00 PM — Homer rushes out at 5pm sharp."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: End of shift — Homer OUT")
    pool, queue_name = await get_queue_pool("homer")
    try:
        await pool.enqueue_job("rush_out_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def evening_handoff() -> None:
    """5:30 PM — Lenny & Carl shift handoff."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Evening shift handoff")
    pool, queue_name = await get_queue_pool("carl")
    try:
        await pool.enqueue_job("shift_handoff_task", _queue_name=queue_name)
    finally:
        await pool.aclose()


async def night_maintenance_job() -> None:
    """10:00 PM — Automated night maintenance."""
    from app.components.worker.pools import get_queue_pool

    logger.info("Scheduler: Night maintenance")
    pool, queue_name = await get_queue_pool("lenny")
    try:
        await pool.enqueue_job("night_maintenance_task", _queue_name=queue_name)
    finally:
        await pool.aclose()

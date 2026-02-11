"""
Worker tasks registry.

This module collects all available worker tasks and exports them for the arq worker.
"""

from collections.abc import Callable
from typing import Any

from .carl_tasks import (
    file_afternoon_reports_task,
    handle_inspector_task,
    make_announcement_task,
    morning_briefing_task,
    shift_handoff_task,
)
from .charlie_tasks import (
    check_emergency_exits_task,
    log_shift_notes_task,
    monitor_gauges_task,
    restock_break_room_task,
)
from .grimey_tasks import grimey_sim_task
from .homer_tasks import (
    attempt_safety_check_task,
    clock_in_task,
    eat_donut_task,
    go_to_moes_task,
    nap_at_console_task,
    rush_out_task,
)
from .inanimate_rod_tasks import inanimate_rod_sim_task
from .lenny_tasks import (
    check_cooling_tower_task,
    file_report_task,
    morning_inspection_task,
    night_maintenance_task,
    open_plant_task,
    run_diagnostics_task,
)
from .simple_system_tasks import (
    cleanup_temp_files,
    system_health_check,
)
from .simulation_tasks import (
    carl_sim_task,
    charlie_sim_task,
    homer_sim_task,
    lenny_sim_task,
)

# All task functions available to arq workers
TASK_FUNCTIONS: list[Callable[..., Any]] = [
    # Homer tasks
    eat_donut_task,
    nap_at_console_task,
    attempt_safety_check_task,
    clock_in_task,
    go_to_moes_task,
    rush_out_task,
    homer_sim_task,
    # Lenny tasks
    run_diagnostics_task,
    file_report_task,
    check_cooling_tower_task,
    morning_inspection_task,
    open_plant_task,
    night_maintenance_task,
    lenny_sim_task,
    # Carl tasks
    handle_inspector_task,
    file_afternoon_reports_task,
    shift_handoff_task,
    make_announcement_task,
    morning_briefing_task,
    carl_sim_task,
    # Charlie tasks
    monitor_gauges_task,
    restock_break_room_task,
    log_shift_notes_task,
    check_emergency_exits_task,
    charlie_sim_task,
    # Inanimate Rod tasks (system maintenance + simulation)
    system_health_check,
    cleanup_temp_files,
    inanimate_rod_sim_task,
    # Grimey tasks
    grimey_sim_task,
]


def get_task_by_name(task_name: str) -> Callable[..., Any] | None:
    """Get task function by name."""
    for task_func in TASK_FUNCTIONS:
        if task_func.__name__ == task_name:
            return task_func
    return None


def list_available_tasks() -> list[str]:
    """Get list of all available task names."""
    return [task_func.__name__ for task_func in TASK_FUNCTIONS]


def get_queue_functions(queue_type: str) -> list[Callable[..., Any]]:
    """Get task functions specific to a queue type."""
    from typing import cast

    queue_function_map: dict[str, list[Callable[..., Any]]] = {
        "homer": [
            eat_donut_task,
            nap_at_console_task,
            attempt_safety_check_task,
            clock_in_task,
            go_to_moes_task,
            rush_out_task,
            homer_sim_task,
        ],
        "lenny": [
            run_diagnostics_task,
            file_report_task,
            check_cooling_tower_task,
            morning_inspection_task,
            open_plant_task,
            night_maintenance_task,
            lenny_sim_task,
        ],
        "carl": [
            handle_inspector_task,
            file_afternoon_reports_task,
            shift_handoff_task,
            make_announcement_task,
            morning_briefing_task,
            carl_sim_task,
        ],
        "charlie": [
            monitor_gauges_task,
            restock_break_room_task,
            log_shift_notes_task,
            check_emergency_exits_task,
            charlie_sim_task,
        ],
        "inanimate_rod": [
            system_health_check,
            cleanup_temp_files,
            inanimate_rod_sim_task,
        ],
        "grimey": [
            grimey_sim_task,
        ],
    }

    return cast(list[Callable[..., Any]], queue_function_map.get(queue_type, []))


def get_queue_for_task(task_name: str) -> str:
    """Get the appropriate queue type for a given task."""
    task_queue_map = {
        # Homer tasks
        "eat_donut_task": "homer",
        "nap_at_console_task": "homer",
        "attempt_safety_check_task": "homer",
        "clock_in_task": "homer",
        "go_to_moes_task": "homer",
        "rush_out_task": "homer",
        "homer_sim_task": "homer",
        # Lenny tasks
        "run_diagnostics_task": "lenny",
        "file_report_task": "lenny",
        "check_cooling_tower_task": "lenny",
        "morning_inspection_task": "lenny",
        "open_plant_task": "lenny",
        "night_maintenance_task": "lenny",
        "lenny_sim_task": "lenny",
        # Carl tasks
        "handle_inspector_task": "carl",
        "file_afternoon_reports_task": "carl",
        "shift_handoff_task": "carl",
        "make_announcement_task": "carl",
        "morning_briefing_task": "carl",
        "carl_sim_task": "carl",
        # Charlie tasks
        "monitor_gauges_task": "charlie",
        "restock_break_room_task": "charlie",
        "log_shift_notes_task": "charlie",
        "check_emergency_exits_task": "charlie",
        "charlie_sim_task": "charlie",
        # Inanimate Rod tasks
        "system_health_check": "inanimate_rod",
        "cleanup_temp_files": "inanimate_rod",
        "inanimate_rod_sim_task": "inanimate_rod",
        # Grimey tasks
        "grimey_sim_task": "grimey",
    }

    return task_queue_map.get(task_name, "inanimate_rod")

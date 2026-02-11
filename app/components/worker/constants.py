"""
Worker component constants.

Springfield Nuclear Power Plant worker queue and task constants.
"""


class QueueNames:
    """Worker queue identifiers."""

    HOMER = "homer"
    LENNY = "lenny"
    CARL = "carl"
    CHARLIE = "charlie"
    INANIMATE_ROD = "inanimate_rod"
    GRIMEY = "grimey"


class TaskNames:
    """Worker task function names — must match actual function names in code."""

    # Homer tasks
    EAT_DONUT = "eat_donut_task"
    NAP_AT_CONSOLE = "nap_at_console_task"
    ATTEMPT_SAFETY_CHECK = "attempt_safety_check_task"
    CLOCK_IN = "clock_in_task"
    GO_TO_MOES = "go_to_moes_task"
    RUSH_OUT = "rush_out_task"

    # Lenny tasks
    RUN_DIAGNOSTICS = "run_diagnostics_task"
    FILE_REPORT = "file_report_task"
    CHECK_COOLING_TOWER = "check_cooling_tower_task"
    MORNING_INSPECTION = "morning_inspection_task"
    OPEN_PLANT = "open_plant_task"
    NIGHT_MAINTENANCE = "night_maintenance_task"

    # Carl tasks
    HANDLE_INSPECTOR = "handle_inspector_task"
    FILE_AFTERNOON_REPORTS = "file_afternoon_reports_task"
    SHIFT_HANDOFF = "shift_handoff_task"
    MAKE_ANNOUNCEMENT = "make_announcement_task"
    MORNING_BRIEFING = "morning_briefing_task"

    # Charlie tasks
    MONITOR_GAUGES = "monitor_gauges_task"
    RESTOCK_BREAK_ROOM = "restock_break_room_task"
    LOG_SHIFT_NOTES = "log_shift_notes_task"
    CHECK_EMERGENCY_EXITS = "check_emergency_exits_task"

    # Inanimate Rod tasks (system maintenance + simulation)
    SYSTEM_HEALTH_CHECK = "system_health_check"
    CLEANUP_TEMP_FILES = "cleanup_temp_files"
    INANIMATE_ROD_SIM = "inanimate_rod_sim_task"

    # Grimey tasks
    GRIMEY_SIM = "grimey_sim_task"

    # Simulation tasks
    HOMER_SIM = "homer_sim_task"
    LENNY_SIM = "lenny_sim_task"
    CARL_SIM = "carl_sim_task"
    CHARLIE_SIM = "charlie_sim_task"

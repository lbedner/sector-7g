"""Column widths and thresholds the tabs share."""

from app.components.frontend.controls import (
    DataTableColumn,
)

OVERVIEW_BAR_CHART_LIMIT = 10
STAT_LABEL_WIDTH = 150
_EXC_COLUMNS = [
    DataTableColumn("Exception", style="primary"),
    DataTableColumn("Message", style="body"),
    DataTableColumn("Count", width=80, style="secondary"),
    DataTableColumn("Latest", width=150, style="secondary"),
]


def _format_latency(ms: float) -> str:
    """Format latency value for display."""
    if ms == 0:
        return "0 ms"
    if ms < 1:
        return f"{ms:.2f} ms"
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{ms / 1000:.2f} s"

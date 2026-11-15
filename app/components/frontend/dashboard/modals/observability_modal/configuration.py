"""What this project told Logfire to do."""

import flet as ft

from app.components.frontend.controls import (
    BodyText,
    SecondaryText,
)
from app.components.frontend.dashboard.modals.observability_modal.shared import (
    STAT_LABEL_WIDTH,
)
from app.components.frontend.theme import AegisTheme as Theme
from app.services.system.models import ComponentStatus


class ConfigurationSection(ft.Container):
    """Configuration section showing observability connection info."""

    def __init__(self, component_data: ComponentStatus, page: ft.Page) -> None:
        super().__init__()
        self.padding = Theme.Spacing.MD

        metadata = component_data.metadata or {}

        service_name = metadata.get("service_name", "unknown")
        send_to_logfire = metadata.get("send_to_logfire", False)
        cloud_status = "Active" if send_to_logfire else "Local only"
        query_api = (
            "Available" if metadata.get("query_api_available") else "Not configured"
        )
        project_url = metadata.get("project_url") or ""

        def _make_row(label: str, value: str) -> ft.Row:
            return ft.Row(
                [
                    SecondaryText(
                        f"{label}:",
                        weight=Theme.Typography.WEIGHT_SEMIBOLD,
                        width=STAT_LABEL_WIDTH,
                    ),
                    BodyText(value),
                ],
                spacing=Theme.Spacing.MD,
            )

        rows: list[ft.Control] = [
            _make_row("Service Name", service_name),
            _make_row("Cloud Status", cloud_status),
            _make_row("Query API", query_api),
        ]

        # Project URL row - clickable link if configured
        if project_url:
            url = project_url

            def _open_url(e: ft.ControlEvent, target_url: str = url) -> None:
                if e.page:
                    e.page.launch_url(target_url)

            link_text = ft.Text(
                project_url,
                size=Theme.Typography.BODY,
                color=Theme.Colors.INFO,
            )

            rows.append(
                ft.Row(
                    [
                        SecondaryText(
                            "Project URL:",
                            weight=Theme.Typography.WEIGHT_SEMIBOLD,
                            width=STAT_LABEL_WIDTH,
                        ),
                        ft.GestureDetector(
                            content=link_text,
                            on_tap=_open_url,
                            mouse_cursor=ft.MouseCursor.CLICK,
                        ),
                    ],
                    spacing=Theme.Spacing.MD,
                )
            )
        else:
            rows.append(_make_row("Project URL", "Not configured"))

        self.content = ft.Column(rows, spacing=Theme.Spacing.SM)


class ConfigTab(ft.Container):
    """Configuration tab showing observability connection info."""

    def __init__(self, component_data: ComponentStatus, page: ft.Page) -> None:
        super().__init__()
        self.content = ft.Column(
            [ConfigurationSection(component_data, page)],
            scroll=ft.ScrollMode.AUTO,
        )
        self.padding = ft.padding.all(Theme.Spacing.SM)
        self.expand = True

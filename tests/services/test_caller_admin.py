"""Whether a tool call acts for an admin (``shared.deps.caller_is_admin``):
what its runner bound (MCP: the token's admin claim), else its owner by
the one admin rule (``is_admin``), else, with no auth service, whoever
reaches the app."""

from app.core.tools import acting_as
from app.services.shared.deps import caller_is_admin


async def test_what_the_runner_bound_decides() -> None:
    with acting_as(None, "mcp:cli", admin=True):
        assert await caller_is_admin()
    with acting_as(None, "mcp:cli", admin=False):
        assert not await caller_is_admin()


async def test_without_auth_whoever_reaches_the_app_is_the_operator() -> None:
    with acting_as(None, "assistant"):
        assert await caller_is_admin()

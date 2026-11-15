"""FastAPI dependencies more than one service injects.

``get_owner_user_id`` centralizes owner scoping in one place: it resolves to
the authenticated user's id when the auth service is present, else ``None``
(single-user / standalone) - so route handlers stay auth-agnostic and never
repeat the auth guard per endpoint. ``get_admin_actor`` does the same for
an operator's change (a restart, a secret set, a deploy): an admin with
auth; without it, only where ``operator_refusal`` allows. Every write action
depends on it (or on Overseer's page-side twin, ``overseer_actor``), and a
UI hides its write controls where ``operator_refusal`` says why not.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status

from app.core import exposure
from app.core.tools import current_admin

# Without auth, an operator's change is asked only at these (``refusal_at``).
LOOPBACK = frozenset({"localhost", "127.0.0.1", "::1"})

NO_AUTH_REFUSAL = (
    "Read only: with no auth service, operator changes are made only on the "
    "local dev build, at localhost. Add auth (aegis add auth) to make them "
    "here as an admin."
)


@dataclass(frozen=True)
class Actor:
    """Who made a change: the signed-in user with the auth service; nobody
    in particular without it (the local dev build's own operator)."""

    id: int | None = None
    email: str | None = None
    name: str | None = None

    @property
    def label(self) -> str:
        """Who to name in a record of the change."""
        return self.email or "anonymous"


def operator_refusal(request: Request) -> str | None:
    """Why ``request`` may not make an operator's change, None when it may
    (``refusal_at`` the address it was sent to, from its page's
    ``Origin``). A page hides its write controls with this line; the
    write itself is refused by ``get_admin_actor``."""
    return refusal_at(str(request.url), request.headers.get("origin"))


def actor_of(user: None = None) -> Actor:
    """Nobody signs in: a change is anyone's."""
    return Actor()


def refusal_at(url: str, origin: str | None = None) -> str | None:
    """Why an operator's change asked at ``url`` (from a page at ``origin``,
    when a browser names one) is refused, None when it may be made: no
    auth service, so only the undeployed dev build (``BUILD_ID`` not yet
    stamped by ``aegis deploy``), asked at a loopback name. The address
    asked at, not the caller's: in Docker a browser on the laptop arrives
    from the bridge gateway, and so does one on the LAN. A LAN address, a
    domain, a rebound DNS name or another site's page is refused."""
    asked = [url] if origin is None else [url, origin]
    if not exposure.deployed() and all(urlsplit(u).hostname in LOOPBACK for u in asked):
        return None
    return NO_AUTH_REFUSAL


async def get_admin_actor(request: Request) -> Actor:
    """No auth service: an operator's change only where ``operator_refusal``
    allows it (403 elsewhere, saying why), by nobody in particular."""
    if refused := operator_refusal(request):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=refused)
    return Actor()


async def get_admin_reader() -> None:
    """An operator's read across every owner: nobody signs in, so anyone
    reading Overseer may (its writes stay behind ``get_admin_actor``)."""


async def get_owner_user_id() -> int | None:
    """No auth service - single-user, so rows are unscoped."""
    return None


# Nobody signs in, so a route that also serves anonymous callers scopes
# the same way.
get_optional_owner_user_id = get_owner_user_id


async def caller_is_admin() -> bool:
    """Whether the tool call being run acts for an admin: what its runner
    bound (``current_admin``: MCP's token, the CLI's shell, an admin-only
    socket), else anyone, with no one to sign in."""
    bound = current_admin.get()
    if bound is not None:
        return bound
    return True

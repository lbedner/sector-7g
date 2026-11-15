"""Who may use Overseer, and what its routes read with: the one place that
knows whether the stack has auth or a database.

With the auth service, admins only (``is_admin``), on every page, stream
and action. Applied once, to the pages router, so a page or partial added
later cannot forget it; tests/web/test_overseer_admin_gate.py walks them
all as a signed-in non-admin. Signed out, a page goes to the login and
anything else (a partial, a stream) is 401. Signed in but not an admin, a
page renders the refusal, which says how to get in, and anything else is a
plain 403. The user lookup is the request's own (``get_optional_user``),
shared with the route's, so it costs no query; the session it opens closes
when the handler returns, before a stream's body is sent (FastAPI 0.116,
pinned in pyproject), so a stream holds no connection.

Without auth, Overseer is open to read: whoever reaches the app may use
it, like any route a stack serves without auth. Its writes (every method
but a read, ``overseer_gate``; ``overseer_actor`` and the API's
``get_admin_actor`` too) are made only on the local dev build
(``operator_refusal``), and their controls hidden elsewhere.
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.services.shared.deps import get_admin_actor, operator_refusal

# A page's database session: the request's own (``get_async_db``), so a
# section reading on it never waits on a second one's lock.
Db = AsyncSession
overseer_db = get_async_db

Viewer = None


async def viewer() -> None:
    """Nobody signs in."""
    return None


# What only reads: anything else is a write.
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


async def overseer_gate(request: Request) -> None:
    """No auth service: everyone may read Overseer; every write (any other
    method, on every page and partial) only where ``operator_refusal``
    allows it, 403 elsewhere, saying why."""
    if request.method in SAFE_METHODS:
        return
    if refused := operator_refusal(request):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=refused)


async def overseer_socket_gate() -> None:
    """No auth service: a live call's socket is open, as every route is."""
    return None


def session_id(request: Request) -> None:
    """No sign-in, so no session."""
    return None


def session_expires(request: Request) -> None:
    """No sign-in, so no session cookie."""
    return None


def add_refusal_page(app: FastAPI) -> None:
    """No auth service: nobody is refused."""


async def user_names(db: Any, ids: list[str]) -> dict[str, str]:
    """No auth service, so no users to name."""
    return {}


# Who makes an Overseer change (a secret set, a post written): the API's
# rule itself, the local dev build's operator or nobody (403).
overseer_actor = get_admin_actor

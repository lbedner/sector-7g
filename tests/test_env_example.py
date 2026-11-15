"""`.env.example` is what a fresh `.env` is copied from, so it must boot.

A key Settings does not declare stops the app at import; a SQLite URL in a
Postgres project starts it on the wrong database, every migration failing.
"""

from pathlib import Path

from dotenv import dotenv_values

from app.core.config import Settings

ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"


def test_settings_accept_every_key() -> None:
    Settings(_env_file=ENV_EXAMPLE)


def test_points_at_postgres() -> None:
    url = dotenv_values(ENV_EXAMPLE)["DATABASE_URL"] or ""
    assert url.startswith("postgresql://"), url

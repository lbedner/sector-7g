"""Seed Springfield Nuclear Power Plant characters

Revision ID: 002
Revises: 001
Create Date: 2026-02-10 03:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

# Pre-hashed password for "springfield" using bcrypt via app/core/security.py
HASHED_PASSWORD = "$2b$12$buReOwHLL3AxSdJmpycuU.LlSGggzXTDOHWQQ/iWU7Qp0n5Cd34mC"

CHARACTERS = [
    {
        "email": "homer@springfield-nuclear.com",
        "full_name": "Homer Simpson",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "burns@springfield-nuclear.com",
        "full_name": "Charles Montgomery Burns",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "smithers@springfield-nuclear.com",
        "full_name": "Waylon Smithers",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "lenny@springfield-nuclear.com",
        "full_name": "Lenny Leonard",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "carl@springfield-nuclear.com",
        "full_name": "Carl Carlson",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "grimey@springfield-nuclear.com",
        "full_name": "Frank Grimes",
        "is_active": False,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "charlie@springfield-nuclear.com",
        "full_name": "Charlie",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
    {
        "email": "rod@springfield-nuclear.com",
        "full_name": "Inanimate Carbon Rod",
        "is_active": True,
        "hashed_password": HASHED_PASSWORD,
    },
]


def upgrade() -> None:
    """Seed Springfield Nuclear Power Plant characters."""
    for char in CHARACTERS:
        op.execute(
            f"""
            INSERT INTO "user"
                (email, full_name, is_active, hashed_password, created_at)
            VALUES (
                '{char["email"]}',
                '{char["full_name"]}',
                {char["is_active"]},
                '{char["hashed_password"]}',
                NOW()
            )
            ON CONFLICT (email) DO NOTHING
            """
        )


def downgrade() -> None:
    """Remove Springfield characters."""
    emails = ", ".join(f"'{c['email']}'" for c in CHARACTERS)
    op.execute(f'DELETE FROM "user" WHERE email IN ({emails})')

"""User table delta for databases created before the 0.10 template.

Revision ID: 006
Revises: 005

Adds the account-lockout and soft-delete columns the 0.10 auth model
queries. Guarded per column: a fresh database already has these from
001, so each add is skipped when the column exists.
"""

import sqlalchemy as sa

from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None
aegis_stamp_signature = ("column", "user", "deleted_at")

_NEW_COLUMNS = [
    sa.Column(
        "failed_login_attempts",
        sa.Integer(),
        nullable=False,
        server_default=sa.text("0"),
    ),
    sa.Column("locked_until", sa.DateTime(), nullable=True),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
]


def _existing_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {col["name"] for col in inspector.get_columns("user")}


def upgrade() -> None:
    existing = _existing_columns()
    for column in _NEW_COLUMNS:
        if column.name not in existing:
            op.add_column("user", column)


def downgrade() -> None:
    existing = _existing_columns()
    for column in reversed(_NEW_COLUMNS):
        if column.name in existing:
            op.drop_column("user", column.name)

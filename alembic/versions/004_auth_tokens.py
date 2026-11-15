"""Auth token tables (password reset, email verification, refresh)

Revision ID: 002
Revises: 001
Create Date: 2026-09-02 03:47:35.395032

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create auth_tokens service tables."""

    # Create password_reset_token table
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )

    op.create_index(
        op.f("ix_password_reset_token_user_id"), "password_reset_token", ["user_id"]
    )

    op.create_index(
        op.f("ix_password_reset_token_token"),
        "password_reset_token",
        ["token"],
        unique=True,
    )

    # Create email_verification_token table
    op.create_table(
        "email_verification_token",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )

    op.create_index(
        op.f("ix_email_verification_token_user_id"),
        "email_verification_token",
        ["user_id"],
    )

    op.create_index(
        op.f("ix_email_verification_token_token"),
        "email_verification_token",
        ["token"],
        unique=True,
    )

    # Create refresh_token table
    op.create_table(
        "refresh_token",
        sa.Column("token", sa.String(64), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("family_id", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(32), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("token"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )

    op.create_index(op.f("ix_refresh_token_user_id"), "refresh_token", ["user_id"])

    op.create_index(op.f("ix_refresh_token_family_id"), "refresh_token", ["family_id"])

    op.create_index(op.f("ix_refresh_token_source"), "refresh_token", ["source"])


def downgrade() -> None:
    """Reverse auth_tokens migration."""

    op.drop_index(op.f("ix_refresh_token_user_id"), table_name="refresh_token")

    op.drop_index(op.f("ix_refresh_token_family_id"), table_name="refresh_token")

    op.drop_index(op.f("ix_refresh_token_source"), table_name="refresh_token")

    op.drop_table("refresh_token")

    op.drop_index(
        op.f("ix_email_verification_token_user_id"),
        table_name="email_verification_token",
    )

    op.drop_index(
        op.f("ix_email_verification_token_token"), table_name="email_verification_token"
    )

    op.drop_table("email_verification_token")

    op.drop_index(
        op.f("ix_password_reset_token_user_id"), table_name="password_reset_token"
    )

    op.drop_index(
        op.f("ix_password_reset_token_token"), table_name="password_reset_token"
    )

    op.drop_table("password_reset_token")

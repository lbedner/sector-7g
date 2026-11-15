"""Auth service tables

Revision ID: 001
Revises: None
Create Date: 2026-09-02 03:47:35.388290

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create auth service tables."""

    # Create user table
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, default=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, default=0),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_user_email"),
        "user",
        ["email"],
        unique=True,
        sqlite_where=sa.text("deleted_at IS NULL"),
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_index(op.f("ix_user_deleted_at"), "user", ["deleted_at"])

    # Create user_oauth_identity table
    op.create_table(
        "user_oauth_identity",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_user_id", sa.String(128), nullable=False),
        sa.Column("provider_username", sa.String(128), nullable=True),
        sa.Column("provider_email", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.CheckConstraint(
            "provider IN ('github', 'google')", name="ck_user_oauth_identity_provider"
        ),
    )

    op.create_index(
        op.f("uq_user_oauth_identity_provider_pid"),
        "user_oauth_identity",
        ["provider", "provider_user_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_user_oauth_identity_user_id"), "user_oauth_identity", ["user_id"]
    )


def downgrade() -> None:
    """Reverse auth migration."""

    op.drop_index(
        op.f("uq_user_oauth_identity_provider_pid"), table_name="user_oauth_identity"
    )

    op.drop_index(
        op.f("ix_user_oauth_identity_user_id"), table_name="user_oauth_identity"
    )

    op.drop_table("user_oauth_identity")

    op.drop_index(op.f("ix_user_email"), table_name="user")

    op.drop_index(op.f("ix_user_deleted_at"), table_name="user")

    op.drop_table("user")

"""Scheduler job execution history

Revision ID: 003
Revises: 002
Create Date: 2026-09-02 03:47:35.401343

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create scheduler service tables."""
    op.execute('CREATE SCHEMA IF NOT EXISTS "scheduler"')

    # Create job_execution table
    op.create_table(
        "job_execution",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("job_id", sa.String(191), nullable=False),
        sa.Column("job_name", sa.String(255), nullable=False, default=""),
        sa.Column("scheduled_run_time", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, default="running"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="scheduler",
    )

    op.create_index(
        op.f("ix_job_execution_job_id"), "job_execution", ["job_id"], schema="scheduler"
    )

    op.create_index(
        op.f("ix_job_execution_started_at"),
        "job_execution",
        ["started_at"],
        schema="scheduler",
    )

    op.create_index(
        op.f("ix_job_execution_status"), "job_execution", ["status"], schema="scheduler"
    )

    op.create_index(
        op.f("ix_job_execution_job_started"),
        "job_execution",
        ["job_id", "started_at"],
        schema="scheduler",
    )


def downgrade() -> None:
    """Reverse scheduler migration."""

    op.drop_index(
        op.f("ix_job_execution_job_id"), table_name="job_execution", schema="scheduler"
    )

    op.drop_index(
        op.f("ix_job_execution_started_at"),
        table_name="job_execution",
        schema="scheduler",
    )

    op.drop_index(
        op.f("ix_job_execution_status"), table_name="job_execution", schema="scheduler"
    )

    op.drop_index(
        op.f("ix_job_execution_job_started"),
        table_name="job_execution",
        schema="scheduler",
    )

    op.drop_table("job_execution", schema="scheduler")

"""Auth service tables

Revision ID: 001
Revises: None
Create Date: 2026-02-10 02:10:58.002584

"""
from datetime import UTC, datetime

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create auth service tables."""

    # Create user table
    op.create_table(
        'user',



        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),



        sa.Column('email', sa.String(), nullable=False),



        sa.Column('full_name', sa.String(), nullable=True),



        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),



        sa.Column('hashed_password', sa.String(), nullable=False),



        sa.Column('created_at', sa.DateTime(), nullable=False),



        sa.Column('updated_at', sa.DateTime(), nullable=True),


        sa.PrimaryKeyConstraint('id')



    )

    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)




def downgrade() -> None:
    """Drop auth service tables."""


    op.drop_index(op.f('ix_user_email'), table_name='user')

    op.drop_table('user')

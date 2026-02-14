"""Add candidate current_position and current_company columns

Revision ID: 002
Revises: 001
Create Date: 2026-02-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add current_position and current_company columns to candidates table
    op.add_column('candidates', sa.Column('current_position', sa.String(length=255), nullable=True))
    op.add_column('candidates', sa.Column('current_company', sa.String(length=255), nullable=True))
    # Create indexes for the new columns
    op.create_index(op.f('ix_candidates_current_position'), 'candidates', ['current_position'], unique=False)
    op.create_index(op.f('ix_candidates_current_company'), 'candidates', ['current_company'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_candidates_current_company'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_current_position'), table_name='candidates')
    # Drop columns
    op.drop_column('candidates', 'current_company')
    op.drop_column('candidates', 'current_position')
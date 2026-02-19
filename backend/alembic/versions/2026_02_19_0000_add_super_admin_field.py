"""Add super admin field to users

Revision ID: 2026_02_19_0000_add_super_admin_field
Revises: 08a9327b717a
Create Date: 2026-02-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_02_19_0000_add_super_admin_field'
down_revision = '08a9327b717a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_super_admin column to users table
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), nullable=False, default=False, index=True))


def downgrade() -> None:
    # Drop is_super_admin column from users table
    op.drop_column('users', 'is_super_admin')
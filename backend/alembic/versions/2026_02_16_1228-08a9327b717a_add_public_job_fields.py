"""Add public job fields

Revision ID: 08a9327b717a
Revises: c10e3e0d79dd
Create Date: 2026-02-16 12:28:06.903303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08a9327b717a'
down_revision = 'c10e3e0d79dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add public job fields to jobs table
    op.add_column('jobs', sa.Column('is_public', sa.Boolean(), nullable=False, default=False, index=True))
    op.add_column('jobs', sa.Column('public_slug', sa.String(255), nullable=True, unique=True, index=True))
    op.add_column('jobs', sa.Column('share_count', sa.Integer(), nullable=False, default=0))
    op.add_column('jobs', sa.Column('share_metadata', sa.JSON(), nullable=False, default={}))
    op.add_column('jobs', sa.Column('og_image_url', sa.String(500), nullable=True))
    op.add_column('jobs', sa.Column('published_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('view_count', sa.Integer(), nullable=False, default=0))
    op.add_column('jobs', sa.Column('show_salary_public', sa.Boolean(), nullable=False, default=False))
    
    # Create unique index on public_slug
    op.create_unique_constraint('uq_jobs_public_slug', 'jobs', ['public_slug'])
    # Create index on is_public
    op.create_index('ix_jobs_is_public', 'jobs', ['is_public'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_jobs_is_public')
    op.drop_constraint('uq_jobs_public_slug', 'jobs')
    
    # Drop columns
    op.drop_column('jobs', 'show_salary_public')
    op.drop_column('jobs', 'view_count')
    op.drop_column('jobs', 'published_at')
    op.drop_column('jobs', 'og_image_url')
    op.drop_column('jobs', 'share_metadata')
    op.drop_column('jobs', 'share_count')
    op.drop_column('jobs', 'public_slug')
    op.drop_column('jobs', 'is_public')

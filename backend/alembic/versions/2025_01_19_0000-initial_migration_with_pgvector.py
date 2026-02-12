"""Initial migration with pgvector

Revision ID: 001
Revises: 
Create Date: 2025-01-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('subdomain', sa.String(), nullable=True),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subdomain')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'])
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'])
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('job_type', sa.String(), nullable=False),
        sa.Column('experience_level', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', postgresql.JSONB(), nullable=True),
        sa.Column('responsibilities', postgresql.JSONB(), nullable=True),
        sa.Column('benefits', postgresql.JSONB(), nullable=True),
        sa.Column('salary_range_min', sa.Integer(), nullable=True),
        sa.Column('salary_range_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('hiring_manager_id', sa.UUID(), nullable=True),
        sa.Column('embeddings', Vector(1536), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closes_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['hiring_manager_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_embeddings', 'jobs', ['embeddings'], postgresql_using='ivfflat')
    op.create_index(op.f('ix_jobs_organization_id'), 'jobs', ['organization_id'])
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'])
    op.create_index(op.f('ix_jobs_title'), 'jobs', ['title'])
    
    # Create candidates table
    op.create_table('candidates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('linkedin_url', sa.String(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('portfolio_url', sa.String(), nullable=True),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('parsed_resume', postgresql.JSONB(), nullable=True),
        sa.Column('skills', postgresql.JSONB(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('current_title', sa.String(), nullable=True),
        sa.Column('current_company', sa.String(), nullable=True),
        sa.Column('education', postgresql.JSONB(), nullable=True),
        sa.Column('certifications', postgresql.JSONB(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('embeddings', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_candidates_embeddings', 'candidates', ['embeddings'], postgresql_using='ivfflat')
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'])
    op.create_index(op.f('ix_candidates_full_name'), 'candidates', ['full_name'])
    op.create_index(op.f('ix_candidates_organization_id'), 'candidates', ['organization_id'])
    
    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('stage', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('screening_score', sa.Float(), nullable=True),
        sa.Column('screening_notes', postgresql.JSONB(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('assigned_to', sa.UUID(), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'candidate_id', name='uq_job_candidate')
    )
    op.create_index(op.f('ix_applications_candidate_id'), 'applications', ['candidate_id'])
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'])
    op.create_index(op.f('ix_applications_organization_id'), 'applications', ['organization_id'])
    op.create_index(op.f('ix_applications_status'), 'applications', ['status'])
    
    # Create interviews table
    op.create_table('interviews',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('interview_type', sa.String(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('meeting_link', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('interviewer_ids', postgresql.JSONB(), nullable=True),
        sa.Column('feedback', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_application_id'), 'interviews', ['application_id'])
    op.create_index(op.f('ix_interviews_organization_id'), 'interviews', ['organization_id'])
    op.create_index(op.f('ix_interviews_scheduled_at'), 'interviews', ['scheduled_at'])
    
    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('assessment_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('questions', postgresql.JSONB(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responses', postgresql.JSONB(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('evaluated_by', sa.UUID(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evaluated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_application_id'), 'assessments', ['application_id'])
    op.create_index(op.f('ix_assessments_organization_id'), 'assessments', ['organization_id'])
    
    # Create communications table
    op.create_table('communications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('communication_type', sa.String(), nullable=False),
        sa.Column('direction', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('sent_by', sa.UUID(), nullable=True),
        sa.Column('sent_to', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communications_application_id'), 'communications', ['application_id'])
    op.create_index(op.f('ix_communications_organization_id'), 'communications', ['organization_id'])
    
    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('integration_type', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('credentials', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integrations_organization_id'), 'integrations', ['organization_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_integrations_organization_id'), table_name='integrations')
    op.drop_table('integrations')
    
    op.drop_index(op.f('ix_communications_organization_id'), table_name='communications')
    op.drop_index(op.f('ix_communications_application_id'), table_name='communications')
    op.drop_table('communications')
    
    op.drop_index(op.f('ix_assessments_organization_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_application_id'), table_name='assessments')
    op.drop_table('assessments')
    
    op.drop_index(op.f('ix_interviews_scheduled_at'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_organization_id'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_application_id'), table_name='interviews')
    op.drop_table('interviews')
    
    op.drop_index(op.f('ix_applications_status'), table_name='applications')
    op.drop_index(op.f('ix_applications_organization_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_candidate_id'), table_name='applications')
    op.drop_table('applications')
    
    op.drop_index(op.f('ix_candidates_organization_id'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_full_name'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_email'), table_name='candidates')
    op.drop_index('idx_candidates_embeddings', table_name='candidates')
    op.drop_table('candidates')
    
    op.drop_index(op.f('ix_jobs_title'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_organization_id'), table_name='jobs')
    op.drop_index('idx_jobs_embeddings', table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_table('organizations')
    
    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')

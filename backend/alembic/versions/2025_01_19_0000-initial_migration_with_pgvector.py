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
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'])
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('last_login', sa.String(), nullable=True),
        sa.Column('google_id', sa.String(), nullable=True),
        sa.Column('microsoft_id', sa.String(), nullable=True),
        sa.Column('linkedin_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('microsoft_id'),
        sa.UniqueConstraint('linkedin_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    
    # Create organization_members table
    op.create_table('organization_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('permissions', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_members_organization_id'), 'organization_members', ['organization_id'])
    op.create_index(op.f('ix_organization_members_user_id'), 'organization_members', ['user_id'])
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('responsibilities', sa.Text(), nullable=True),
        sa.Column('benefits', sa.Text(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('is_remote', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('job_type', sa.String(), nullable=False),
        sa.Column('experience_level', sa.String(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('openings', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('skills_required', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('skills_preferred', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('is_internal', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('application_deadline', sa.String(), nullable=True),
        sa.Column('settings', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_embedding', 'jobs', ['embedding'], postgresql_using='ivfflat')
    op.create_index(op.f('ix_jobs_organization_id'), 'jobs', ['organization_id'])
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'])
    op.create_index(op.f('ix_jobs_title'), 'jobs', ['title'])
    
    # Create job_stages table
    op.create_table('job_stages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_stages_job_id'), 'job_stages', ['job_id'])
    
    # Create candidates table
    op.create_table('candidates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
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
        sa.Column('embeddings', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_candidates_embeddings', 'candidates', ['embeddings'], postgresql_using='ivfflat')
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'])
    op.create_index(op.f('ix_candidates_organization_id'), 'candidates', ['organization_id'])
    
    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_stage', sa.UUID(), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('application_answers', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('ai_match_score', sa.Float(), nullable=True),
        sa.Column('ai_insights', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('ai_strengths', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('ai_concerns', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('ai_recommendation', sa.String(), nullable=True),
        sa.Column('manual_score', sa.Float(), nullable=True),
        sa.Column('applied_at', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('referrer_id', sa.UUID(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_archived', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['current_stage'], ['job_stages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id', 'candidate_id', name='uq_job_candidate')
    )
    op.create_index(op.f('ix_applications_candidate_id'), 'applications', ['candidate_id'])
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'])
    op.create_index(op.f('ix_applications_status'), 'applications', ['status'])
    
    # Create application_activities table
    op.create_table('application_activities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('activity_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_activities_application_id'), 'application_activities', ['application_id'])
    
    # Create application_notes table
    op.create_table('application_notes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_private', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('mentions', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_notes_application_id'), 'application_notes', ['application_id'])
    
    # Create application_scores table
    op.create_table('application_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), server_default=sa.text('10.0'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_scores_application_id'), 'application_scores', ['application_id'])
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_application_id'), 'interviews', ['application_id'])
    op.create_index(op.f('ix_interviews_scheduled_at'), 'interviews', ['scheduled_at'])
    
    # Create interview_participants table
    op.create_table('interview_participants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('interview_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_participants_interview_id'), 'interview_participants', ['interview_id'])
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evaluated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_application_id'), 'assessments', ['application_id'])
    
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communications_application_id'), 'communications', ['application_id'])
    
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
    
    op.drop_index(op.f('ix_communications_application_id'), table_name='communications')
    op.drop_table('communications')
    
    op.drop_index(op.f('ix_assessments_application_id'), table_name='assessments')
    op.drop_table('assessments')
    
    op.drop_index(op.f('ix_interview_participants_interview_id'), table_name='interview_participants')
    op.drop_table('interview_participants')
    
    op.drop_index(op.f('ix_interviews_application_id'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_scheduled_at'), table_name='interviews')
    op.drop_table('interviews')
    
    op.drop_index(op.f('ix_application_scores_application_id'), table_name='application_scores')
    op.drop_table('application_scores')
    
    op.drop_index(op.f('ix_application_notes_application_id'), table_name='application_notes')
    op.drop_table('application_notes')
    
    op.drop_index(op.f('ix_application_activities_application_id'), table_name='application_activities')
    op.drop_table('application_activities')
    
    op.drop_index(op.f('ix_applications_candidate_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_status'), table_name='applications')
    op.drop_table('applications')
    
    op.drop_index(op.f('ix_candidates_email'), table_name='candidates')
    op.drop_index(op.f('ix_candidates_organization_id'), table_name='candidates')
    op.drop_index('idx_candidates_embeddings', table_name='candidates')
    op.drop_table('candidates')
    
    op.drop_index(op.f('ix_job_stages_job_id'), table_name='job_stages')
    op.drop_table('job_stages')
    
    op.drop_index(op.f('ix_jobs_title'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_organization_id'), table_name='jobs')
    op.drop_index('idx_jobs_embedding', table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index(op.f('ix_organization_members_organization_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_user_id'), table_name='organization_members')
    op.drop_table('organization_members')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_table('organizations')
    
    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')

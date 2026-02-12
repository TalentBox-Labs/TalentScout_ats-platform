"""Update schema to match current models

Revision ID: 002
Revises: 001
Create Date: 2026-02-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update jobs table to match current Job model
    # Rename salary columns
    op.alter_column('jobs', 'salary_range_min', new_column_name='salary_min', existing_type=sa.Integer())
    op.alter_column('jobs', 'salary_range_max', new_column_name='salary_max', existing_type=sa.Integer())

    # Change requirements/responsibilities/benefits from JSONB to Text
    op.alter_column('jobs', 'requirements', existing_type=postgresql.JSONB(), type_=sa.Text())
    op.alter_column('jobs', 'responsibilities', existing_type=postgresql.JSONB(), type_=sa.Text())
    op.alter_column('jobs', 'benefits', existing_type=postgresql.JSONB(), type_=sa.Text())

    # Add new columns for Job model
    op.add_column('jobs', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('jobs', sa.Column('is_remote', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('jobs', sa.Column('experience_level', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('openings', sa.Integer(), server_default=sa.text('1'), nullable=True))
    op.add_column('jobs', sa.Column('skills_required', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True))
    op.add_column('jobs', sa.Column('skills_preferred', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True))
    op.add_column('jobs', sa.Column('is_internal', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('jobs', sa.Column('application_deadline', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('settings', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True))

    # Add foreign key constraint for created_by
    op.create_foreign_key('fk_jobs_created_by', 'jobs', 'users', ['created_by'], ['id'], ondelete='SET NULL')

    # Update candidates table to match current Candidate model
    # Split full_name into first_name and last_name
    op.add_column('candidates', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('last_name', sa.String(), nullable=True))

    # Migrate data from full_name to first_name/last_name (simplified - assumes single word names)
    op.execute("""
        UPDATE candidates
        SET first_name = split_part(full_name, ' ', 1),
            last_name = CASE WHEN array_length(string_to_array(full_name, ' '), 1) > 1
                            THEN array_to_string((string_to_array(full_name, ' '))[2:], ' ')
                            ELSE ''
                        END
    """)

    # Make first_name/last_name not null after data migration
    op.alter_column('candidates', 'first_name', nullable=False)
    op.alter_column('candidates', 'last_name', nullable=False)

    # Remove old full_name column
    op.drop_column('candidates', 'full_name')

    # Rename embeddings to resume_embedding
    op.alter_column('candidates', 'embeddings', new_column_name='resume_embedding', existing_type=Vector(1536))

    # Remove old columns that are no longer in the model
    op.drop_column('candidates', 'resume_text')
    op.drop_column('candidates', 'skills')
    op.drop_column('candidates', 'experience_years')
    op.drop_column('candidates', 'current_title')
    op.drop_column('candidates', 'current_company')
    op.drop_column('candidates', 'education')
    op.drop_column('candidates', 'certifications')

    # Add new columns for Candidate model
    op.add_column('candidates', sa.Column('timezone', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('headline', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('candidates', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('portfolio_url', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('twitter_url', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('website_url', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('total_experience_years', sa.Integer(), nullable=True))
    op.add_column('candidates', sa.Column('ai_summary', sa.Text(), nullable=True))
    op.add_column('candidates', sa.Column('quality_score', sa.Float(), nullable=True))
    op.add_column('candidates', sa.Column('desired_salary_min', sa.Integer(), nullable=True))
    op.add_column('candidates', sa.Column('desired_salary_max', sa.Integer(), nullable=True))
    op.add_column('candidates', sa.Column('desired_locations', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True))
    op.add_column('candidates', sa.Column('open_to_remote', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('candidates', sa.Column('available_from', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('notice_period_days', sa.Integer(), nullable=True))
    op.add_column('candidates', sa.Column('opted_in_marketing', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('candidates', sa.Column('gdpr_consent', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('candidates', sa.Column('gdpr_consent_date', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('source_id', sa.UUID(), nullable=True))
    op.add_column('candidates', sa.Column('source_details', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True))

    # Create new tables for related models
    # Job stages table
    op.create_table('job_stages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Candidate sources table
    op.create_table('candidate_sources',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('cost_per_candidate', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Candidate experiences table
    op.create_table('candidate_experiences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('is_current', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Candidate education table
    op.create_table('candidate_education',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('institution', sa.String(), nullable=False),
        sa.Column('degree', sa.String(), nullable=True),
        sa.Column('field_of_study', sa.String(), nullable=True),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('grade', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Candidate skills table
    op.create_table('candidate_skills',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('proficiency_level', sa.Integer(), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Update applications table to match current Application model
    op.add_column('applications', sa.Column('current_stage', sa.UUID(), nullable=True))
    op.add_column('applications', sa.Column('cover_letter', sa.Text(), nullable=True))
    op.add_column('applications', sa.Column('application_answers', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True))
    op.add_column('applications', sa.Column('ai_match_score', sa.Float(), nullable=True))
    op.add_column('applications', sa.Column('ai_insights', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True))
    op.add_column('applications', sa.Column('ai_strengths', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True))
    op.add_column('applications', sa.Column('ai_concerns', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True))
    op.add_column('applications', sa.Column('ai_recommendation', sa.String(), nullable=True))
    op.add_column('applications', sa.Column('manual_score', sa.Float(), nullable=True))
    op.add_column('applications', sa.Column('referrer_id', sa.UUID(), nullable=True))

    # Remove old columns
    op.drop_column('applications', 'stage')
    op.drop_column('applications', 'screening_score')
    op.drop_column('applications', 'screening_notes')
    op.drop_column('applications', 'ai_summary')
    op.drop_column('applications', 'match_score')
    op.drop_column('applications', 'organization_id')
    op.drop_column('applications', 'assigned_to')

    # Add foreign key constraints
    op.create_foreign_key('fk_applications_current_stage', 'applications', 'job_stages', ['current_stage'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_applications_referrer', 'applications', 'users', ['referrer_id'], ['id'], ondelete='SET NULL')

    # Create application activities table
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

    # Create application notes table
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

    # Create application scores table
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

    # Create screening templates table
    op.create_table('screening_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('questions', postgresql.JSONB(), nullable=False),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('passing_score', sa.Float(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_ai_generated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('template_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sent_at', sa.String(), nullable=True),
        sa.Column('started_at', sa.String(), nullable=True),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('expires_at', sa.String(), nullable=True),
        sa.Column('time_taken_minutes', sa.Integer(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['screening_templates.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token')
    )

    # Create assessment responses table
    op.create_table('assessment_responses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('response_data', postgresql.JSONB(), nullable=True),
        sa.Column('file_urls', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=True),
        sa.Column('max_points', sa.Float(), nullable=True),
        sa.Column('ai_evaluation', sa.Text(), nullable=True),
        sa.Column('ai_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create assessment scores table
    op.create_table('assessment_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('scored_by', sa.UUID(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('percentage_score', sa.Float(), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(), nullable=True),
        sa.Column('is_ai_scored', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('ai_insights', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scored_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create interviews table
    op.create_table('interviews',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('interviewer_id', sa.UUID(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('interview_type', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('meeting_link', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create communications table
    op.create_table('communications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=True),
        sa.Column('recipient_id', sa.UUID(), nullable=True),
        sa.Column('application_id', sa.UUID(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Update indexes for new column names
    op.create_index('idx_candidates_resume_embedding', 'candidates', ['resume_embedding'], postgresql_using='ivfflat')
    op.drop_index('idx_candidates_embeddings', table_name='candidates')


def downgrade() -> None:
    # This downgrade is complex and potentially destructive, so we'll leave it minimal
    # In a real scenario, you'd implement proper downgrade logic
    pass
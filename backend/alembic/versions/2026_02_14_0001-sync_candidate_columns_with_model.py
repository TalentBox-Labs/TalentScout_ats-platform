"""Sync candidate columns with current SQLAlchemy model.

Revision ID: 003
Revises: 002
Create Date: 2026-02-14 00:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table = "candidates"
    existing_tables = set(inspector.get_table_names())

    # Basic/profile columns
    if not _has_column(inspector, table, "timezone"):
        op.add_column(table, sa.Column("timezone", sa.String(length=50), nullable=True))
    if not _has_column(inspector, table, "headline"):
        op.add_column(table, sa.Column("headline", sa.String(length=500), nullable=True))
    if not _has_column(inspector, table, "summary"):
        op.add_column(table, sa.Column("summary", sa.Text(), nullable=True))
    if not _has_column(inspector, table, "avatar_url"):
        op.add_column(table, sa.Column("avatar_url", sa.String(length=500), nullable=True))
    if not _has_column(inspector, table, "twitter_url"):
        op.add_column(table, sa.Column("twitter_url", sa.String(length=500), nullable=True))
    if not _has_column(inspector, table, "website_url"):
        op.add_column(table, sa.Column("website_url", sa.String(length=500), nullable=True))

    # Parsed/AI columns
    if not _has_column(inspector, table, "total_experience_years"):
        op.add_column(table, sa.Column("total_experience_years", sa.Integer(), nullable=True))
    if not _has_column(inspector, table, "resume_embedding"):
        op.add_column(table, sa.Column("resume_embedding", Vector(1536), nullable=True))
    if not _has_column(inspector, table, "ai_summary"):
        op.add_column(table, sa.Column("ai_summary", sa.Text(), nullable=True))
    if not _has_column(inspector, table, "quality_score"):
        op.add_column(table, sa.Column("quality_score", sa.Float(), nullable=True))

    # Job-search/privacy/source columns
    if not _has_column(inspector, table, "desired_salary_min"):
        op.add_column(table, sa.Column("desired_salary_min", sa.Integer(), nullable=True))
    if not _has_column(inspector, table, "desired_salary_max"):
        op.add_column(table, sa.Column("desired_salary_max", sa.Integer(), nullable=True))
    if not _has_column(inspector, table, "desired_locations"):
        op.add_column(table, sa.Column("desired_locations", sa.JSON(), nullable=True))
    if not _has_column(inspector, table, "open_to_remote"):
        op.add_column(table, sa.Column("open_to_remote", sa.Boolean(), nullable=True))
    if not _has_column(inspector, table, "available_from"):
        op.add_column(table, sa.Column("available_from", sa.String(length=255), nullable=True))
    if not _has_column(inspector, table, "notice_period_days"):
        op.add_column(table, sa.Column("notice_period_days", sa.Integer(), nullable=True))
    if not _has_column(inspector, table, "is_active"):
        op.add_column(table, sa.Column("is_active", sa.Boolean(), nullable=True))
    if not _has_column(inspector, table, "opted_in_marketing"):
        op.add_column(table, sa.Column("opted_in_marketing", sa.Boolean(), nullable=True))
    if not _has_column(inspector, table, "gdpr_consent"):
        op.add_column(table, sa.Column("gdpr_consent", sa.Boolean(), nullable=True))
    if not _has_column(inspector, table, "gdpr_consent_date"):
        op.add_column(table, sa.Column("gdpr_consent_date", sa.String(length=255), nullable=True))
    if not _has_column(inspector, table, "source_id"):
        op.add_column(table, sa.Column("source_id", sa.UUID(), nullable=True))
        if "candidate_sources" in existing_tables:
            op.create_foreign_key(
                "fk_candidates_source_id_candidate_sources",
                "candidates",
                "candidate_sources",
                ["source_id"],
                ["id"],
                ondelete="SET NULL",
            )
    if not _has_column(inspector, table, "source_details"):
        op.add_column(table, sa.Column("source_details", sa.JSON(), nullable=True))

    # Helpful indexes used by current model
    inspector = sa.inspect(bind)
    if not _has_index(inspector, table, "ix_candidates_current_position"):
        op.create_index("ix_candidates_current_position", table, ["current_position"], unique=False)
    if not _has_index(inspector, table, "ix_candidates_current_company"):
        op.create_index("ix_candidates_current_company", table, ["current_company"], unique=False)
    if not _has_index(inspector, table, "ix_candidates_linkedin_url"):
        op.create_index("ix_candidates_linkedin_url", table, ["linkedin_url"], unique=False)


def downgrade() -> None:
    # No-op for safety in local/dev stabilization flow.
    pass

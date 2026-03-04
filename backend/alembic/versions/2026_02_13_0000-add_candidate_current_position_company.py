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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("candidates")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("candidates")}

    if "current_position" not in existing_columns:
        op.add_column("candidates", sa.Column("current_position", sa.String(length=255), nullable=True))
    if "current_company" not in existing_columns:
        op.add_column("candidates", sa.Column("current_company", sa.String(length=255), nullable=True))

    if op.f("ix_candidates_current_position") not in existing_indexes:
        op.create_index(op.f("ix_candidates_current_position"), "candidates", ["current_position"], unique=False)
    if op.f("ix_candidates_current_company") not in existing_indexes:
        op.create_index(op.f("ix_candidates_current_company"), "candidates", ["current_company"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("candidates")}
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("candidates")}

    if op.f("ix_candidates_current_company") in existing_indexes:
        op.drop_index(op.f("ix_candidates_current_company"), table_name="candidates")
    if op.f("ix_candidates_current_position") in existing_indexes:
        op.drop_index(op.f("ix_candidates_current_position"), table_name="candidates")

    if "current_company" in existing_columns:
        op.drop_column("candidates", "current_company")
    if "current_position" in existing_columns:
        op.drop_column("candidates", "current_position")

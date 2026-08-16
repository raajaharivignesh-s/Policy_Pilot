"""add document extracted fields

Revision ID: b1c2d3e4f5a6
Revises: 60eea737a824
Create Date: 2026-08-16 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "60eea737a824"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("document_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("extracted_fields", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "extracted_fields")
    op.drop_column("documents", "document_type")

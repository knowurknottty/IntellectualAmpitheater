"""run prompt persistence

Stores the dispatched prompt on the run row so a seat's later runs in the
same thread can assemble real conversation context (prior prompts plus the
seat's own prior outputs) instead of hashing a placeholder. Nullable: rows
written before this migration keep prompt=None and are skipped by context
assembly rather than reconstructed from digests.

Revision ID: 0003_run_prompt
Revises: 0002_thread_created_at
Create Date: 2026-10-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_run_prompt"
down_revision = "0002_thread_created_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("runs", sa.Column("prompt", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("runs", "prompt")

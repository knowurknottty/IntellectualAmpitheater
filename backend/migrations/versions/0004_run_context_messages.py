"""run context messages

Stores the exact assembled message list sent to the provider for each run,
so "show me what it saw" renders persisted fact instead of reconstructing
(and possibly mis-rebuilding) history at read time. Nullable: runs written
before this migration have no recorded list and report it as unavailable.

Revision ID: 0004_run_context_messages
Revises: 0003_run_prompt
Create Date: 2026-10-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_run_context_messages"
down_revision = "0003_run_prompt"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("runs", sa.Column("context_messages", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("runs", "context_messages")

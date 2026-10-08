"""run kind + source lineage

Marks runs produced by machinery rather than ordinary dispatch (reveal
rounds, counterfactual replays) so conversation context assembly can keep
them out of a seat's history, and records the source run a derived run
answers to. Ordinary dispatch remains the default.

Revision ID: 0005_run_kind_lineage
Revises: 0004_run_context_messages
Create Date: 2026-10-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_run_kind_lineage"
down_revision = "0004_run_context_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("runs", sa.Column("run_kind", sa.String(), nullable=True))
    op.add_column("runs", sa.Column("source_run_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("runs", "source_run_id")
    op.drop_column("runs", "run_kind")

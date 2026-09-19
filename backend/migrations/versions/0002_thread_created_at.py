"""thread created_at

Adds a stable ordering key to threads. `runs.thread_id` has no foreign key in
the live schema, so legacy runs (e.g. `thread_local_default`) can exist without a
threads row; those are surfaced by the listing as implicit threads. This
migration deliberately does NOT add a foreign key and does NOT rewrite any run.

SQLite's ALTER TABLE ADD COLUMN rejects CURRENT_TIMESTAMP as a default, so the
column is added nullable with no server default, existing rows are backfilled
explicitly, and new rows receive the ORM-side default.

Revision ID: 0002_thread_created_at
Revises: 0001_initial
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_thread_created_at"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("threads", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE threads SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")


def downgrade() -> None:
    op.drop_column("threads", "created_at")

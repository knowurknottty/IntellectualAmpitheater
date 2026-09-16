"""initial IntelAMP durable schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "seats",
        sa.Column("seat_id", sa.String(), primary_key=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("provider_id", sa.String(), nullable=False),
        sa.Column("model_id", sa.String(), nullable=False),
        sa.Column("provider_family", sa.String(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("context_view_id", sa.String(), nullable=False),
        sa.Column("tool_policy_id", sa.String(), nullable=False),
        sa.Column("generation_config", sa.JSON(), nullable=False),
        sa.Column("independence_mode", sa.String(), nullable=False),
        sa.Column("visibility_policy", sa.String(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
    )
    op.create_table(
        "threads",
        sa.Column("thread_id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("schema_version", sa.Integer(), nullable=False),
    )
    op.create_table(
        "turns",
        sa.Column("turn_id", sa.String(), primary_key=True),
        sa.Column("thread_id", sa.String(), sa.ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_turn_id", sa.String(), nullable=True),
        sa.Column("author_seat_id", sa.String(), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
    )
    op.create_table(
        "runs",
        sa.Column("run_id", sa.String(), primary_key=True),
        sa.Column("dispatch_id", sa.String(), nullable=True),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("turn_parent", sa.String(), nullable=True),
        sa.Column("seat_id", sa.String(), nullable=False),
        sa.Column("provider_id", sa.String(), nullable=False),
        sa.Column("model_id", sa.String(), nullable=False),
        sa.Column("provider_family", sa.String(), nullable=True),
        sa.Column("request_digest", sa.String(), nullable=False),
        sa.Column("context_view_digest", sa.String(), nullable=False),
        sa.Column("evidence_root_digest", sa.String(), nullable=False),
        sa.Column("tool_policy_digest", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_token_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminal_state", sa.String(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("provider_request_id", sa.String(), nullable=True),
        sa.Column("output_digest", sa.String(), nullable=True),
        sa.Column("failure_class", sa.String(), nullable=True),
        sa.Column("retry_of_run_id", sa.String(), nullable=True),
        sa.Column("schema_version", sa.Integer(), nullable=False),
    )
    op.create_index("ix_runs_dispatch_id", "runs", ["dispatch_id"])
    op.create_index("ix_runs_seat_id", "runs", ["seat_id"])
    op.create_table(
        "run_events",
        sa.Column("event_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("runs.run_id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.UniqueConstraint("run_id", "sequence", name="uq_run_event_sequence"),
    )
    op.create_index("ix_run_events_run_id", "run_events", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_run_events_run_id", table_name="run_events")
    op.drop_table("run_events")
    op.drop_index("ix_runs_seat_id", table_name="runs")
    op.drop_index("ix_runs_dispatch_id", table_name="runs")
    op.drop_table("runs")
    op.drop_table("turns")
    op.drop_table("threads")
    op.drop_table("seats")

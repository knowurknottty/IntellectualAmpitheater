from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class SeatModel(Base):
    __tablename__ = "seats"
    seat_id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    provider_id: Mapped[str] = mapped_column(String, nullable=False)
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_family: Mapped[str | None] = mapped_column(String, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    context_view_id: Mapped[str] = mapped_column(String, nullable=False, default="default")
    tool_policy_id: Mapped[str] = mapped_column(String, nullable=False, default="none")
    generation_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    independence_mode: Mapped[str] = mapped_column(String, nullable=False, default="ordinary")
    visibility_policy: Mapped[str] = mapped_column(String, nullable=False, default="default")
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ThreadModel(Base):
    __tablename__ = "threads"
    thread_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TurnModel(Base):
    __tablename__ = "turns"
    turn_id: Mapped[str] = mapped_column(String, primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=False)
    parent_turn_id: Mapped[str | None] = mapped_column(String, nullable=True)
    author_seat_id: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class RunModel(Base):
    __tablename__ = "runs"
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    dispatch_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    thread_id: Mapped[str] = mapped_column(String, nullable=False)
    turn_parent: Mapped[str | None] = mapped_column(String, nullable=True)
    seat_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String, nullable=False)
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_family: Mapped[str | None] = mapped_column(String, nullable=True)
    request_digest: Mapped[str] = mapped_column(String, nullable=False)
    context_view_digest: Mapped[str] = mapped_column(String, nullable=False)
    evidence_root_digest: Mapped[str] = mapped_column(String, nullable=False)
    tool_policy_digest: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_token_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    terminal_state: Mapped[str | None] = mapped_column(String, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    output_digest: Mapped[str | None] = mapped_column(String, nullable=True)
    failure_class: Mapped[str | None] = mapped_column(String, nullable=True)
    retry_of_run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class RunEventModel(Base):
    __tablename__ = "run_events"
    __table_args__ = (UniqueConstraint("run_id", "sequence", name="uq_run_event_sequence"),)
    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

from datetime import UTC, datetime

import pytest
from sqlalchemy import text

from intelamp.contracts import SeatCreate, TerminalState
from intelamp.database import Base, create_engine_and_session
from intelamp.repositories import EventRepository, RunRepository, SeatRepository


@pytest.fixture
async def db(tmp_path):
    path = tmp_path / "intelamp.sqlite3"
    engine, sessions = create_engine_and_session(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine, sessions
    await engine.dispose()


@pytest.mark.asyncio
async def test_sqlite_file_uses_wal_mode(db) -> None:
    engine, _ = db
    async with engine.connect() as conn:
        mode = (await conn.execute(text("PRAGMA journal_mode"))).scalar_one()
    assert str(mode).lower() == "wal"


@pytest.mark.asyncio
async def test_seat_crud_persists_explicit_order(db) -> None:
    _, sessions = db
    repo = SeatRepository(sessions)
    second = await repo.create(SeatCreate(display_name="Second", provider_id="p", model_id="m2", order_index=1))
    first = await repo.create(SeatCreate(display_name="First", provider_id="p", model_id="m1", order_index=0))
    assert [seat.seat_id for seat in await repo.list()] == [first.seat_id, second.seat_id]
    updated = await repo.update(first.seat_id, {"display_name": "Primary"})
    assert updated.display_name == "Primary"
    await repo.delete(second.seat_id)
    assert [seat.display_name for seat in await repo.list()] == ["Primary"]


@pytest.mark.asyncio
async def test_run_events_are_monotonic_and_partial_chunks_are_durable(db) -> None:
    _, sessions = db
    runs = RunRepository(sessions)
    events = EventRepository(sessions)
    run = await runs.create(
        thread_id="thread_1",
        turn_parent=None,
        seat_id="seat_1",
        provider_id="p",
        model_id="m",
        provider_family="family",
        request_digest="sha256:req",
        context_view_digest="sha256:ctx",
        evidence_root_digest="sha256:evidence",
        tool_policy_digest="sha256:tools",
    )
    first = await events.append(run.run_id, "chunk", {"text": "hel"})
    second = await events.append(run.run_id, "chunk", {"text": "lo"})
    assert (first.sequence, second.sequence) == (1, 2)
    after = await events.list_after(run.run_id, 0)
    assert [event.data["text"] for event in after] == ["hel", "lo"]


@pytest.mark.asyncio
async def test_terminal_run_cannot_be_rewritten_completed(db) -> None:
    _, sessions = db
    runs = RunRepository(sessions)
    run = await runs.create(
        thread_id="thread_1",
        turn_parent=None,
        seat_id="seat_1",
        provider_id="p",
        model_id="m",
        provider_family=None,
        request_digest="sha256:req",
        context_view_digest="sha256:ctx",
        evidence_root_digest="sha256:evidence",
        tool_policy_digest="sha256:tools",
    )
    await runs.finalize(run.run_id, TerminalState.STREAM_INTERRUPTED, completed_at=datetime.now(UTC))
    with pytest.raises(ValueError, match="already terminal"):
        await runs.finalize(run.run_id, TerminalState.COMPLETED, completed_at=datetime.now(UTC))

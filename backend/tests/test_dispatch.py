import asyncio

import pytest

from intelamp.contracts import (
    CapabilityState,
    DispatchRequest,
    FailureClass,
    ProviderCapabilities,
    ProviderDefinition,
    SeatCreate,
    TerminalState,
)
from intelamp.database import Base, create_engine_and_session
from intelamp.dispatch import DispatchEngine
from intelamp.providers.base import ProviderStreamEvent, ProviderStreamEventType
from intelamp.providers.openai_compat import ProviderAdapterError
from intelamp.registry import ProviderRegistry
from intelamp.repositories import EventRepository, RunRepository, SeatRepository


class ScriptedAdapter:
    def __init__(self, chunks=("ok",), *, delay=0.01, failure: ProviderAdapterError | None = None):
        self.chunks = list(chunks)
        self.delay = delay
        self.failure = failure
        self.active = 0
        self.max_active = 0
        self.calls = 0

    async def list_models(self):
        return ["model"]

    async def stream_chat(self, request, cancel_event):
        self.calls += 1
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            for chunk in self.chunks:
                await asyncio.sleep(self.delay)
                if cancel_event.is_set():
                    raise ProviderAdapterError(FailureClass.CANCELLED_BY_USER, "cancelled")
                yield ProviderStreamEvent(event_type=ProviderStreamEventType.DELTA, data={"text": chunk})
            if self.failure is not None:
                raise self.failure
            yield ProviderStreamEvent(event_type=ProviderStreamEventType.DONE, data={})
        finally:
            self.active -= 1


def provider(provider_id: str, concurrency: int = 1) -> ProviderDefinition:
    return ProviderDefinition(
        provider_id=provider_id,
        display_name=provider_id,
        adapter="test",
        base_url="http://test.invalid/v1",
        provider_family="test-family",
        max_concurrent_requests=concurrency,
        capabilities=ProviderCapabilities(streaming=CapabilityState.SUPPORTED),
    )


async def harness(tmp_path, definitions, adapters):
    engine_db, sessions = create_engine_and_session(f"sqlite+aiosqlite:///{tmp_path / 'dispatch.sqlite3'}")
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    seats = SeatRepository(sessions)
    runs = RunRepository(sessions)
    events = EventRepository(sessions)
    registry = ProviderRegistry(definitions, adapters=adapters)
    dispatch = DispatchEngine(seats=seats, runs=runs, events=events, registry=registry)
    return engine_db, seats, runs, events, dispatch


@pytest.mark.asyncio
async def test_provider_semaphore_caps_ordinary_seat_concurrency(tmp_path):
    adapter = ScriptedAdapter(chunks=("a", "b"), delay=0.02)
    db, seats, runs, events, dispatch = await harness(tmp_path, [provider("p", 1)], {"p": adapter})
    try:
        one = await seats.create(SeatCreate(display_name="One", provider_id="p", model_id="m1"))
        two = await seats.create(SeatCreate(display_name="Two", provider_id="p", model_id="m2"))
        accepted = await dispatch.dispatch(DispatchRequest(thread_id="t", prompt="hello", seat_ids=[one.seat_id, two.seat_id]))
        await asyncio.gather(*(dispatch.wait(run_id) for run_id in accepted.run_ids))
        assert adapter.max_active == 1
        assert [((await runs.get(run_id)).terminal_state) for run_id in accepted.run_ids] == [
            TerminalState.COMPLETED.value,
            TerminalState.COMPLETED.value,
        ]
    finally:
        await db.dispose()


@pytest.mark.asyncio
async def test_sibling_failure_does_not_erase_success(tmp_path):
    good = ScriptedAdapter(chunks=("good",))
    bad = ScriptedAdapter(failure=ProviderAdapterError(FailureClass.PROVIDER_PROTOCOL_ERROR, "boom"))
    db, seats, runs, events, dispatch = await harness(
        tmp_path,
        [provider("good"), provider("bad")],
        {"good": good, "bad": bad},
    )
    try:
        good_seat = await seats.create(SeatCreate(display_name="Good", provider_id="good", model_id="m"))
        bad_seat = await seats.create(SeatCreate(display_name="Bad", provider_id="bad", model_id="m"))
        accepted = await dispatch.dispatch(DispatchRequest(thread_id="t", prompt="hello", seat_ids=[good_seat.seat_id, bad_seat.seat_id]))
        await asyncio.gather(*(dispatch.wait(run_id) for run_id in accepted.run_ids))
        rows = [await runs.get(run_id) for run_id in accepted.run_ids]
        by_provider = {row.provider_id: row for row in rows}
        assert by_provider["good"].terminal_state == TerminalState.COMPLETED.value
        assert by_provider["good"].output_digest is not None
        assert by_provider["bad"].terminal_state == TerminalState.FAILED.value
        assert by_provider["bad"].failure_class == FailureClass.PROVIDER_PROTOCOL_ERROR.value
    finally:
        await db.dispose()


@pytest.mark.asyncio
async def test_user_cancellation_is_terminal_and_preserves_prior_chunks(tmp_path):
    adapter = ScriptedAdapter(chunks=("first", "second", "third"), delay=0.04)
    db, seats, runs, events, dispatch = await harness(tmp_path, [provider("p")], {"p": adapter})
    try:
        seat = await seats.create(SeatCreate(display_name="One", provider_id="p", model_id="m"))
        accepted = await dispatch.dispatch(DispatchRequest(thread_id="t", prompt="hello", seat_ids=[seat.seat_id]))
        run_id = accepted.run_ids[0]
        await asyncio.sleep(0.06)
        await dispatch.cancel(run_id)
        await dispatch.wait(run_id)
        row = await runs.get(run_id)
        assert row.terminal_state == TerminalState.CANCELLED_BY_USER.value
        assert row.failure_class == FailureClass.CANCELLED_BY_USER.value
        chunks = [event.data["text"] for event in await events.list_after(run_id, 0) if event.event_type == "chunk"]
        assert chunks == ["first"]
        assert row.output_digest is not None
    finally:
        await db.dispose()


@pytest.mark.asyncio
async def test_stream_interruption_preserves_partial_output(tmp_path):
    adapter = ScriptedAdapter(
        chunks=("partial",),
        failure=ProviderAdapterError(FailureClass.STREAM_INTERRUPTED, "wire broke"),
    )
    db, seats, runs, events, dispatch = await harness(tmp_path, [provider("p")], {"p": adapter})
    try:
        seat = await seats.create(SeatCreate(display_name="One", provider_id="p", model_id="m"))
        accepted = await dispatch.dispatch(DispatchRequest(thread_id="t", prompt="hello", seat_ids=[seat.seat_id]))
        run_id = accepted.run_ids[0]
        await dispatch.wait(run_id)
        row = await runs.get(run_id)
        assert row.terminal_state == TerminalState.STREAM_INTERRUPTED.value
        assert row.failure_class == FailureClass.STREAM_INTERRUPTED.value
        chunks = [event.data["text"] for event in await events.list_after(run_id, 0) if event.event_type == "chunk"]
        assert chunks == ["partial"]
        assert row.output_digest is not None
    finally:
        await db.dispose()


@pytest.mark.asyncio
async def test_retry_lineage_is_explicit(tmp_path):
    adapter = ScriptedAdapter(chunks=("ok",))
    db, seats, runs, events, dispatch = await harness(tmp_path, [provider("p")], {"p": adapter})
    try:
        seat = await seats.create(SeatCreate(display_name="One", provider_id="p", model_id="m"))
        request = DispatchRequest(thread_id="t", prompt="hello", seat_ids=[seat.seat_id])
        first = await dispatch.dispatch(request)
        await dispatch.wait(first.run_ids[0])
        second = await dispatch.dispatch(request, retry_of={seat.seat_id: first.run_ids[0]})
        await dispatch.wait(second.run_ids[0])
        second_row = await runs.get(second.run_ids[0])
        assert second_row.retry_of_run_id == first.run_ids[0]
        assert second.run_ids[0] != first.run_ids[0]
    finally:
        await db.dispose()


@pytest.mark.asyncio
async def test_missing_provider_never_substitutes_another_provider(tmp_path):
    fallback = ScriptedAdapter(chunks=("fallback",))
    db, seats, runs, events, dispatch = await harness(tmp_path, [provider("fallback")], {"fallback": fallback})
    try:
        seat = await seats.create(SeatCreate(display_name="Missing", provider_id="not-registered", model_id="wanted-model"))
        accepted = await dispatch.dispatch(DispatchRequest(thread_id="t", prompt="hello", seat_ids=[seat.seat_id]))
        run_id = accepted.run_ids[0]
        await dispatch.wait(run_id)
        row = await runs.get(run_id)
        assert row.provider_id == "not-registered"
        assert row.model_id == "wanted-model"
        assert row.terminal_state == TerminalState.FAILED.value
        assert row.failure_class == FailureClass.PROVIDER_UNAVAILABLE.value
        assert fallback.calls == 0
    finally:
        await db.dispose()

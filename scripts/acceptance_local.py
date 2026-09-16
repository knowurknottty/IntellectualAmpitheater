#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import hashlib
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from intelamp.config import build_registry, load_provider_definitions
from intelamp.contracts import DispatchRequest, GenerationConfig, SeatCreate
from intelamp.database import Base, create_engine_and_session
from intelamp.dispatch import DispatchEngine
from intelamp.repositories import EventRepository, RunRepository, SeatRepository

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "config" / "providers.example.toml"
EVIDENCE = ROOT / "evidence" / "task10-local-acceptance.md"


def output_from(events) -> str:
    return "".join(str(event.data.get("text", "")) for event in events if event.event_type == "chunk")


async def wait_all(engine: DispatchEngine, run_ids: list[str]) -> None:
    await asyncio.gather(*(engine.wait(run_id) for run_id in run_ids))


async def main() -> None:
    definitions = load_provider_definitions(PROVIDERS)
    registry = build_registry(definitions)
    local = registry.get("local-llama")
    if local.adapter is None:
        raise RuntimeError("local llama adapter unavailable")
    models = await local.adapter.list_models()
    if not models:
        raise RuntimeError("local llama server returned no models")
    model_id = models[0]

    with tempfile.TemporaryDirectory(prefix="intelamp-t10-") as tmp:
        db_path = Path(tmp) / "acceptance.sqlite3"
        engine, sessions = create_engine_and_session(f"sqlite+aiosqlite:///{db_path}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        seats = SeatRepository(sessions)
        runs = RunRepository(sessions)
        events = EventRepository(sessions)
        dispatch = DispatchEngine(seats=seats, runs=runs, events=events, registry=registry)

        async def make_seat(name: str, provider_id: str = "local-llama", max_tokens: int = 128):
            return await seats.create(SeatCreate(
                display_name=name,
                provider_id=provider_id,
                model_id=model_id,
                provider_family="local" if provider_id == "local-llama" else "invalid",
                generation_config=GenerationConfig(max_output_tokens=max_tokens),
            ))

        single = await make_seat("Single")
        accepted_single = await dispatch.dispatch(DispatchRequest(thread_id="accept-single", prompt="Reply with exactly ONE_OK.", seat_ids=[single.seat_id]))
        await wait_all(dispatch, accepted_single.run_ids)
        single_row = await runs.get(accepted_single.run_ids[0])
        single_events = await events.list_after(accepted_single.run_ids[0], 0)
        single_output = output_from(single_events)
        assert single_row and single_row.terminal_state == "completed" and "ONE_OK" in single_output

        six = [await make_seat(f"Six-{index + 1}", max_tokens=128) for index in range(6)]
        accepted_six = await dispatch.dispatch(DispatchRequest(thread_id="accept-six", prompt="Reply with exactly SIX_OK.", seat_ids=[seat.seat_id for seat in six]))
        await wait_all(dispatch, accepted_six.run_ids)
        six_rows = [await runs.get(run_id) for run_id in accepted_six.run_ids]
        six_events = [await events.list_after(run_id, 0) for run_id in accepted_six.run_ids]
        six_outputs = [output_from(batch) for batch in six_events]
        assert all(row and row.terminal_state == "completed" for row in six_rows)
        assert all("SIX_OK" in output for output in six_outputs)

        cancel_seat = await make_seat("Cancel", max_tokens=768)
        accepted_cancel = await dispatch.dispatch(DispatchRequest(
            thread_id="accept-cancel",
            prompt="Write a long numbered list of 250 short facts about software testing. Do not stop early.",
            seat_ids=[cancel_seat.seat_id],
        ))
        cancel_run = accepted_cancel.run_ids[0]
        for _ in range(200):
            batch = await events.list_after(cancel_run, 0)
            if any(event.event_type == "chunk" for event in batch):
                break
            await asyncio.sleep(0.025)
        else:
            raise RuntimeError("cancel acceptance never observed a live output chunk")
        assert await dispatch.cancel(cancel_run) is True
        await dispatch.wait(cancel_run)
        cancel_row = await runs.get(cancel_run)
        cancel_events = await events.list_after(cancel_run, 0)
        assert cancel_row and cancel_row.terminal_state == "cancelled_by_user"

        good = await make_seat("Good sibling")
        bad = await make_seat("Invalid sibling", provider_id="missing-provider")
        accepted_mixed = await dispatch.dispatch(DispatchRequest(
            thread_id="accept-mixed",
            prompt="Reply with exactly MIXED_OK.",
            seat_ids=[good.seat_id, bad.seat_id],
        ))
        await wait_all(dispatch, accepted_mixed.run_ids)
        good_row = await runs.get(accepted_mixed.run_ids[0])
        bad_row = await runs.get(accepted_mixed.run_ids[1])
        good_events = await events.list_after(accepted_mixed.run_ids[0], 0)
        bad_events = await events.list_after(accepted_mixed.run_ids[1], 0)
        good_output = output_from(good_events)
        assert good_row and good_row.terminal_state == "completed" and "MIXED_OK" in good_output
        assert bad_row and bad_row.terminal_state == "failed" and bad_row.failure_class == "provider_unavailable"

        observed = datetime.now(UTC).isoformat()
        evidence = f"""# Tranche 0 local acceptance\n\n- observed_at_utc: {observed}\n- endpoint: `http://127.0.0.1:8080/v1`\n- provider_id: `local-llama`\n- model_id: `{model_id}`\n- provider_max_concurrent_requests: `{local.max_concurrent_requests}`\n- credential: none\n\n## One seat\n- run_id: `{accepted_single.run_ids[0]}`\n- terminal_state: `{single_row.terminal_state}`\n- output: `{single_output.strip()}`\n\n## Six seats through provider scheduler\n- run_ids: `{json.dumps(accepted_six.run_ids)}`\n- terminal_states: `{json.dumps([row.terminal_state for row in six_rows if row])}`\n- outputs: `{json.dumps([output.strip() for output in six_outputs])}`\n\n## Cancel in flight\n- run_id: `{cancel_run}`\n- terminal_state: `{cancel_row.terminal_state}`\n- partial_output_sha256: `{hashlib.sha256(output_from(cancel_events).encode()).hexdigest()}`\n- partial_chunk_count: `{sum(event.event_type == "chunk" for event in cancel_events)}`\n\n## Invalid provider beside successful local seat\n- good_run_id: `{accepted_mixed.run_ids[0]}`\n- good_terminal_state: `{good_row.terminal_state}`\n- good_output: `{good_output.strip()}`\n- invalid_run_id: `{accepted_mixed.run_ids[1]}`\n- invalid_terminal_state: `{bad_row.terminal_state}`\n- invalid_failure_class: `{bad_row.failure_class}`\n"""
        EVIDENCE.write_text(evidence, encoding="utf-8")
        print(evidence)
        print("EVIDENCE_SHA256=" + hashlib.sha256(evidence.encode()).hexdigest())
        await engine.dispose()

    aclose = getattr(local.adapter, "aclose", None)
    if aclose is not None:
        await aclose()


if __name__ == "__main__":
    asyncio.run(main())

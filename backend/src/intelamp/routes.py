from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Body, Header
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .contracts import DispatchRequest, FailureClass, GenerationConfig, RunReceipt, SeatCreate, TerminalState, ThreadCreate
from .dispatch import DispatchEngine
from .registry import ProviderRegistry
from .repositories import EventRepository, RunRepository, SeatRepository, ThreadRepository
from .anchoring import seat_anchor_report
from .mirage import mirage_lint
from .voices import compute_effective_voices


@dataclass(slots=True)
class RouteServices:
    seats: SeatRepository
    runs: RunRepository
    events: EventRepository
    threads: ThreadRepository
    registry: ProviderRegistry
    dispatch: DispatchEngine


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


def _receipt_from_row(row) -> RunReceipt:
    if row.terminal_state is None:
        raise ValueError("run is not terminal")
    return RunReceipt(
        schema_version=row.schema_version,
        run_id=row.run_id,
        thread_id=row.thread_id,
        turn_parent=row.turn_parent,
        seat_id=row.seat_id,
        provider_id=row.provider_id,
        model_id=row.model_id,
        provider_family=row.provider_family,
        request_digest=row.request_digest,
        context_view_digest=row.context_view_digest,
        evidence_root_digest=row.evidence_root_digest,
        tool_policy_digest=row.tool_policy_digest,
        started_at=row.started_at,
        first_token_at=row.first_token_at,
        completed_at=row.completed_at,
        terminal_state=TerminalState(row.terminal_state),
        input_tokens=row.input_tokens,
        output_tokens=row.output_tokens,
        provider_request_id=row.provider_request_id,
        output_digest=row.output_digest,
        failure_class=FailureClass(row.failure_class) if row.failure_class else None,
        retry_of_run_id=row.retry_of_run_id,
    )


def create_router(services: RouteServices) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/seats")
    async def list_seats() -> dict[str, Any]:
        return {"seats": [seat.model_dump(mode="json") for seat in await services.seats.list()]}

    @router.post("/seats", status_code=201)
    async def create_seat(seat: SeatCreate):
        return await services.seats.create(seat)

    @router.patch("/seats/{seat_id}")
    async def patch_seat(seat_id: str, changes: dict[str, Any] = Body(...)):
        try:
            return await services.seats.update(seat_id, changes)
        except KeyError:
            return _error(404, "seat_not_found", f"seat not found: {seat_id}")
        except ValueError as exc:
            return _error(422, "seat_update_invalid", str(exc))

    @router.delete("/seats/{seat_id}", status_code=204)
    async def delete_seat(seat_id: str):
        try:
            await services.seats.delete(seat_id)
        except KeyError:
            return _error(404, "seat_not_found", f"seat not found: {seat_id}")
        return Response(status_code=204)

    @router.get("/providers")
    async def list_providers() -> dict[str, Any]:
        providers = []
        for definition in services.registry.definitions():
            providers.append(
                {
                    "provider_id": definition.provider_id,
                    "display_name": definition.display_name,
                    "adapter": definition.adapter,
                    "base_url": definition.base_url,
                    "provider_family": definition.provider_family,
                    "max_concurrent_requests": definition.max_concurrent_requests,
                    "capabilities": definition.capabilities.model_dump(mode="json"),
                    "metadata": definition.metadata,
                }
            )
        return {"providers": providers}

    @router.get("/threads")
    async def list_threads() -> dict[str, Any]:
        return {"threads": [thread.model_dump(mode="json") for thread in await services.threads.list()]}

    @router.post("/threads", status_code=201)
    async def create_thread(payload: ThreadCreate):
        return (await services.threads.create(payload)).model_dump(mode="json")

    @router.get("/threads/{thread_id}")
    async def get_thread(thread_id: str):
        thread = await services.threads.get(thread_id)
        if thread is None:
            return _error(404, "thread_not_found", f"thread not found: {thread_id}")
        return thread.model_dump(mode="json")

    @router.post("/dispatch", status_code=202)
    async def dispatch(request: DispatchRequest):
        try:
            return await services.dispatch.dispatch(request)
        except KeyError as exc:
            return _error(404, "seat_not_found", str(exc))
        except ValueError as exc:
            return _error(422, "dispatch_invalid", str(exc))

    @router.get("/runs/{run_id}/events")
    async def run_events(
        run_id: str,
        last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    ):
        row = await services.runs.get(run_id)
        if row is None:
            return _error(404, "run_not_found", f"run not found: {run_id}")
        try:
            cursor = int(last_event_id) if last_event_id is not None else 0
        except ValueError:
            return _error(400, "last_event_id_invalid", "Last-Event-ID must be an integer")
        if cursor < 0:
            return _error(400, "last_event_id_invalid", "Last-Event-ID must be non-negative")

        async def stream():
            sequence = cursor
            while True:
                batch = await services.events.list_after(run_id, sequence)
                if batch:
                    for event in batch:
                        sequence = event.sequence
                        payload = json.dumps(event.model_dump(mode="json"), separators=(",", ":"))
                        yield f"id: {event.sequence}\nevent: {event.event_type}\ndata: {payload}\n\n"
                    if any(event.event_type == "terminal" for event in batch):
                        break
                    continue
                current = await services.runs.get(run_id)
                if current is None:
                    break
                if current.terminal_state is not None:
                    # REPAIR (SSE silent-break race, confirmed by unit falsifier):
                    # the run is terminal but a terminal event was never appended
                    # (finalize commits state before the event append; a subscriber
                    # that polls inside that window used to get a clean empty
                    # stream and never learn the outcome — the UI seat stayed
                    # "running" forever). Reconstruct a terminal frame from the
                    # durable receipt state. The synthesized frame is marked
                    # `reconstructed: true`; it never invents a terminal state —
                    # it reports the state the run actually has.
                    payload = json.dumps(
                        {
                            "run_id": run_id,
                            "sequence": sequence + 1,
                            "event_type": "terminal",
                            "created_at": current.completed_at.isoformat() if current.completed_at else None,
                            "data": {
                                "terminal_state": current.terminal_state,
                                "failure_class": current.failure_class,
                                "output_digest": current.output_digest,
                                "reconstructed": True,
                            },
                        },
                        separators=(",", ":"),
                    )
                    yield f"id: {sequence + 1}\nevent: terminal\ndata: {payload}\n\n"
                    break
                await asyncio.sleep(0.02)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.post("/runs/{run_id}/cancel", status_code=202)
    async def cancel_run(run_id: str):
        row = await services.runs.get(run_id)
        if row is None:
            return _error(404, "run_not_found", f"run not found: {run_id}")
        requested = await services.dispatch.cancel(run_id)
        return {"run_id": run_id, "cancel_requested": requested}

    @router.get("/threads/{thread_id}/effective-voices")
    async def effective_voices(thread_id: str):
        """Independence-discounted voice count for the thread's latest dispatch."""
        thread = await services.threads.get(thread_id)
        if thread is None:
            return _error(404, "thread_not_found", f"thread not found: {thread_id}")
        rows = await services.runs.latest_dispatch_runs(thread_id)
        result = compute_effective_voices(
            [
                {
                    "run_id": row.run_id,
                    "seat_id": row.seat_id,
                    "provider_id": row.provider_id,
                    "model_id": row.model_id,
                    "terminal_state": row.terminal_state,
                    "context_messages": row.context_messages,
                }
                for row in rows
            ]
        )
        return {"thread_id": thread_id, "dispatch_id": rows[0].dispatch_id if rows else None, **result}

    @router.post("/runs/{run_id}/replay", status_code=202)
    async def replay_run(run_id: str, overrides: dict[str, Any] = Body(...)):
        """Counterfactual Seat: clone a terminal run changing exactly one variable.

        Exactly one of model_id / prompt / generation fields may be supplied,
        and it must actually differ. The new run links back via retry lineage
        and carries a `counterfactual` event naming the changed field, so the
        receipt pair differs in exactly one input.
        """
        replay_fields = {"model_id", "prompt", "temperature", "top_p", "seed", "max_output_tokens", "reasoning_control"}
        source = await services.runs.get(run_id)
        if source is None:
            return _error(404, "run_not_found", f"run not found: {run_id}")
        if source.terminal_state is None:
            return _error(409, "run_not_terminal", f"run is not terminal: {run_id}")
        if source.prompt is None:
            return _error(409, "context_unavailable", "source run has no recorded prompt to replay")
        unknown = set(overrides) - replay_fields
        if unknown:
            return _error(422, "counterfactual_unknown_field", f"unknown replay fields: {sorted(unknown)}")
        if len(overrides) != 1:
            return _error(422, "counterfactual_requires_exactly_one_change", "supply exactly one changed variable")
        field, value = next(iter(overrides.items()))
        seat = await services.seats.get(source.seat_id)
        if seat is None:
            return _error(404, "seat_not_found", f"seat not found: {source.seat_id}")
        current: dict[str, Any] = {
            "model_id": source.model_id,
            "prompt": source.prompt,
            **seat.generation_config.model_dump(mode="json"),
        }
        if value == current.get(field):
            return _error(422, "counterfactual_no_change", f"{field} is unchanged; a counterfactual needs a real difference")
        if field == "model_id" and (not isinstance(value, str) or not value.strip()):
            return _error(422, "counterfactual_invalid_value", "model_id must be a non-empty string")
        if field == "prompt" and (not isinstance(value, str) or not value.strip()):
            return _error(422, "counterfactual_invalid_value", "prompt must be a non-empty string")
        if field not in {"model_id", "prompt"}:
            try:
                GenerationConfig.model_validate({**seat.generation_config.model_dump(mode="json"), field: value})
            except Exception as exc:
                return _error(422, "counterfactual_invalid_value", str(exc))
        new_prompt = value if field == "prompt" else source.prompt
        seat_override = {} if field == "prompt" else {field: value}
        try:
            accepted = await services.dispatch.dispatch(
                DispatchRequest(
                    thread_id=source.thread_id,
                    turn_parent=source.turn_parent,
                    prompt=new_prompt,
                    seat_ids=[source.seat_id],
                ),
                retry_of={source.seat_id: run_id},
                seat_overrides={source.seat_id: seat_override},
                history_before_run_id=run_id,
                run_kind="counterfactual",
                seat_events={
                    source.seat_id: [
                        (
                            "counterfactual",
                            {"source_run_id": run_id, "changed_field": field, "from": current.get(field), "to": value},
                        )
                    ]
                },
            )
        except (KeyError, ValueError) as exc:
            return _error(422, "counterfactual_dispatch_invalid", str(exc))
        return accepted

    @router.post("/dispatch/{dispatch_id}/reveal", status_code=202)
    async def reveal_round(dispatch_id: str):
        """Sealed Reveal: each seat sees its peers' answers and may revise.

        Round one stayed blind (isolated dispatch). This round shows every
        seat the other seats' answers; revisions are new runs (kind=reveal)
        that never enter conversation history. One reveal per dispatch.
        """
        rows = await services.runs.runs_for_dispatch(dispatch_id)
        if not rows:
            return _error(404, "dispatch_not_found", f"dispatch not found: {dispatch_id}")
        completed = [row for row in rows if row.terminal_state == TerminalState.COMPLETED.value and row.prompt]
        if len(completed) < 2:
            return _error(422, "reveal_requires_two_completed", "reveal needs at least two completed seats")
        existing = await services.runs.runs_for_sources([row.run_id for row in completed], run_kind="reveal")
        if existing:
            return _error(409, "reveal_already_run", "this dispatch already had its reveal round")
        outputs = {row.run_id: await services.events.output_text(row.run_id) for row in completed}
        if any(not text.strip() for text in outputs.values()):
            return _error(422, "reveal_requires_outputs", "every completed seat needs output text to reveal")

        explicit: dict[str, list[dict[str, str]]] = {}
        sources: dict[str, str] = {}
        seat_events: dict[str, list] = {}
        for row in completed:
            peers = [other for other in completed if other.run_id != row.run_id]
            peer_block = "\n\n".join(
                f"[{other.model_id} via {other.provider_id}]\n{outputs[other.run_id]}" for other in peers
            )
            instruction = (
                "The other seats answered the same prompt as follows:\n\n"
                f"{peer_block}\n\n"
                "Revise your answer if their answers change yours, or hold it if they do not. "
                "Reply with your final answer only."
            )
            explicit[row.seat_id] = [
                {"role": "user", "content": row.prompt or ""},
                {"role": "assistant", "content": outputs[row.run_id]},
                {"role": "user", "content": instruction},
            ]
            sources[row.seat_id] = row.run_id
            seat_events[row.seat_id] = [
                ("reveal", {"source_dispatch_id": dispatch_id, "source_run_id": row.run_id})
            ]
        accepted = await services.dispatch.dispatch(
            DispatchRequest(
                thread_id=completed[0].thread_id,
                prompt="Reveal round: revise or hold after seeing peer answers.",
                seat_ids=[row.seat_id for row in completed],
            ),
            explicit_messages=explicit,
            source_run_ids=sources,
            run_kind="reveal",
            seat_events=seat_events,
        )
        return accepted

    @router.get("/dispatch/{dispatch_id}/anchoring")
    async def anchoring_report(dispatch_id: str):
        """Per-seat Anchoring Delta for a dispatch's reveal round (exploratory)."""
        rows = await services.runs.runs_for_dispatch(dispatch_id)
        if not rows:
            return _error(404, "dispatch_not_found", f"dispatch not found: {dispatch_id}")
        completed = [row for row in rows if row.terminal_state == TerminalState.COMPLETED.value]
        reveal_runs = await services.runs.runs_for_sources([row.run_id for row in completed], run_kind="reveal")
        reveal_by_source = {row.source_run_id: row for row in reveal_runs}
        outputs = {row.run_id: await services.events.output_text(row.run_id) for row in completed}
        seats_report = []
        for row in completed:
            reveal = reveal_by_source.get(row.run_id)
            revised = await services.events.output_text(reveal.run_id) if reveal and reveal.terminal_state else None
            peers = [outputs[other.run_id] for other in completed if other.run_id != row.run_id]
            seats_report.append(
                seat_anchor_report(
                    seat_id=row.seat_id,
                    model_id=row.model_id,
                    source_run_id=row.run_id,
                    reveal_run_id=reveal.run_id if reveal else None,
                    reveal_state=reveal.terminal_state if reveal else None,
                    original=outputs[row.run_id],
                    revised=revised,
                    peers_original=peers,
                )
            )
        return {
            "dispatch_id": dispatch_id,
            "reveal_dispatch_id": reveal_runs[0].dispatch_id if reveal_runs else None,
            "label": "exploratory: lexical movement toward peers; movement is not correctness",
            "seats": seats_report,
        }

    @router.get("/threads/{thread_id}/mirage")
    async def mirage(thread_id: str):
        """Consensus Mirage Lint over the thread's latest dispatch (advisory)."""
        thread = await services.threads.get(thread_id)
        if thread is None:
            return _error(404, "thread_not_found", f"thread not found: {thread_id}")
        rows = await services.runs.latest_dispatch_runs(thread_id)
        outputs = {row.run_id: await services.events.output_text(row.run_id) for row in rows}
        result = mirage_lint(
            [
                {
                    "run_id": row.run_id,
                    "seat_id": row.seat_id,
                    "provider_id": row.provider_id,
                    "model_id": row.model_id,
                    "terminal_state": row.terminal_state,
                    "context_messages": row.context_messages,
                }
                for row in rows
            ],
            outputs,
        )
        return {"thread_id": thread_id, "dispatch_id": rows[0].dispatch_id if rows else None, **result}

    @router.get("/runs/{run_id}/context")
    async def run_context(run_id: str):
        """The exact message list the provider received for this run.

        Served from the persisted copy written at dispatch time, never
        reconstructed. Legacy runs without a recorded list say so.
        """
        row = await services.runs.get(run_id)
        if row is None:
            return _error(404, "run_not_found", f"run not found: {run_id}")
        return {
            "run_id": row.run_id,
            "context_view_digest": row.context_view_digest,
            "messages": row.context_messages,
        }

    @router.get("/runs/{run_id}/receipt")
    async def receipt(run_id: str):
        row = await services.runs.get(run_id)
        if row is None:
            return _error(404, "run_not_found", f"run not found: {run_id}")
        if row.terminal_state is None:
            return _error(409, "run_not_terminal", f"run is not terminal: {run_id}")
        return _receipt_from_row(row)

    return router

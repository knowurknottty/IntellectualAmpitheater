from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from .capabilities import compile_capabilities
from .contracts import (
    DispatchAccepted,
    DispatchRequest,
    FailureClass,
    SeatRecord,
    TerminalState,
)
from .providers.base import ProviderStreamEventType
from .providers.openai_compat import ProviderAdapterError
from .registry import ProviderRegistry, RegisteredProvider
from .repositories import EventRepository, RunRepository, SeatRepository


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _request_digest(request: DispatchRequest, seat: SeatRecord) -> str:
    return _sha256_json(
        {
            "thread_id": request.thread_id,
            "turn_parent": request.turn_parent,
            "prompt": request.prompt,
            "seat_id": seat.seat_id,
            "provider_id": seat.provider_id,
            "model_id": seat.model_id,
            "generation_config": seat.generation_config.model_dump(mode="json"),
            "requested_capabilities": {
                "required": sorted(request.requested_capabilities.required),
                "optional": sorted(request.requested_capabilities.optional),
            },
        }
    )


def _provider_payload(request: DispatchRequest, seat: SeatRecord) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": seat.model_id,
        "messages": [{"role": "user", "content": request.prompt}],
    }
    generation = seat.generation_config
    if generation.temperature is not None:
        payload["temperature"] = generation.temperature
    if generation.top_p is not None:
        payload["top_p"] = generation.top_p
    if generation.seed is not None:
        payload["seed"] = generation.seed
    if generation.max_output_tokens is not None:
        payload["max_tokens"] = generation.max_output_tokens
    if generation.reasoning_control is not None:
        payload["reasoning_control"] = generation.reasoning_control
    payload["stream_options"] = {"include_usage": True}
    return payload


class DispatchEngine:
    def __init__(
        self,
        *,
        seats: SeatRepository,
        runs: RunRepository,
        events: EventRepository,
        registry: ProviderRegistry,
    ) -> None:
        self._seats = seats
        self._runs = runs
        self._events = events
        self._registry = registry
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._cancel_events: dict[str, asyncio.Event] = {}

    async def dispatch(
        self,
        request: DispatchRequest,
        *,
        retry_of: Mapping[str, str] | None = None,
    ) -> DispatchAccepted:
        retry_of = retry_of or {}
        unexpected_retry_seats = set(retry_of) - set(request.seat_ids)
        if unexpected_retry_seats:
            raise ValueError(f"retry lineage supplied for seats not in dispatch: {sorted(unexpected_retry_seats)}")

        resolved: list[SeatRecord] = []
        for seat_id in request.seat_ids:
            seat = await self._seats.get(seat_id)
            if seat is None:
                raise KeyError(f"seat not found: {seat_id}")
            resolved.append(seat)

        dispatch_id = f"dispatch_{uuid4().hex}"
        run_ids: list[str] = []
        for seat in resolved:
            run = await self._runs.create(
                dispatch_id=dispatch_id,
                thread_id=request.thread_id,
                turn_parent=request.turn_parent,
                seat_id=seat.seat_id,
                provider_id=seat.provider_id,
                model_id=seat.model_id,
                provider_family=seat.provider_family,
                request_digest=_request_digest(request, seat),
                context_view_digest=_sha256_json({"context_view_id": seat.context_view_id}),
                evidence_root_digest=_sha256_json({"evidence": "none:not-selected"}),
                tool_policy_digest=_sha256_json({"tool_policy_id": seat.tool_policy_id}),
                retry_of_run_id=retry_of.get(seat.seat_id),
            )
            await self._events.append(run.run_id, "queued", {"dispatch_id": dispatch_id})
            cancel_event = asyncio.Event()
            self._cancel_events[run.run_id] = cancel_event
            task = asyncio.create_task(
                self._execute_run(run.run_id, request, seat, cancel_event),
                name=f"intelamp:{run.run_id}",
            )
            self._tasks[run.run_id] = task
            run_ids.append(run.run_id)

        return DispatchAccepted(dispatch_id=dispatch_id, run_ids=run_ids)

    async def wait(self, run_id: str) -> None:
        task = self._tasks.get(run_id)
        if task is None:
            row = await self._runs.get(run_id)
            if row is None:
                raise KeyError(run_id)
            return
        await asyncio.shield(task)

    async def cancel(self, run_id: str) -> bool:
        cancel_event = self._cancel_events.get(run_id)
        if cancel_event is None:
            row = await self._runs.get(run_id)
            if row is None:
                raise KeyError(run_id)
            return False
        cancel_event.set()
        return True

    async def _registered_provider(self, seat: SeatRecord) -> RegisteredProvider:
        try:
            registered = self._registry.get(seat.provider_id)
        except KeyError as exc:
            raise ProviderAdapterError(
                FailureClass.PROVIDER_UNAVAILABLE,
                f"provider is not registered: {seat.provider_id}",
            ) from exc
        if registered.adapter is None:
            raise ProviderAdapterError(
                FailureClass.PROVIDER_UNAVAILABLE,
                f"provider adapter is unavailable: {seat.provider_id}",
            )
        return registered

    async def _execute_run(
        self,
        run_id: str,
        request: DispatchRequest,
        seat: SeatRecord,
        cancel_event: asyncio.Event,
    ) -> None:
        chunks: list[str] = []
        input_tokens: int | None = None
        output_tokens: int | None = None
        terminal = TerminalState.COMPLETED
        failure: FailureClass | None = None

        try:
            registered = await self._registered_provider(seat)
            compile_result = compile_capabilities(request.requested_capabilities, registered.definition.capabilities)
            if compile_result.warnings:
                await self._events.append(
                    run_id,
                    "capability_warning",
                    {"issues": [issue.model_dump(mode="json") for issue in compile_result.warnings]},
                )
            if not compile_result.compatible:
                raise ProviderAdapterError(
                    FailureClass.CAPABILITY_MISMATCH,
                    "; ".join(issue.message for issue in compile_result.hard_incompatibilities),
                )

            async with registered.semaphore:
                if cancel_event.is_set():
                    raise ProviderAdapterError(FailureClass.CANCELLED_BY_USER, "request cancelled before provider start")
                await self._events.append(
                    run_id,
                    "running",
                    {"provider_id": seat.provider_id, "model_id": seat.model_id},
                )
                first_token_seen = False
                async for event in registered.adapter.stream_chat(_provider_payload(request, seat), cancel_event):
                    if event.event_type is ProviderStreamEventType.DELTA:
                        text = event.data.get("text")
                        if isinstance(text, str) and text:
                            if not first_token_seen:
                                first_token_seen = True
                                await self._runs.mark_first_token(run_id, datetime.now(UTC))
                            chunks.append(text)
                            await self._events.append(run_id, "chunk", {"text": text})
                    elif event.event_type is ProviderStreamEventType.USAGE:
                        prompt = event.data.get("prompt_tokens")
                        completion = event.data.get("completion_tokens")
                        input_tokens = prompt if isinstance(prompt, int) else input_tokens
                        output_tokens = completion if isinstance(completion, int) else output_tokens
                        await self._events.append(run_id, "usage", dict(event.data))
                    elif event.event_type is ProviderStreamEventType.ERROR:
                        raise ProviderAdapterError(
                            FailureClass.PROVIDER_PROTOCOL_ERROR,
                            "provider emitted an error stream event",
                        )
        except ProviderAdapterError as exc:
            failure = exc.failure_class
            if failure is FailureClass.CANCELLED_BY_USER:
                terminal = TerminalState.CANCELLED_BY_USER
            elif failure is FailureClass.STREAM_INTERRUPTED:
                terminal = TerminalState.STREAM_INTERRUPTED
            else:
                terminal = TerminalState.FAILED
        except asyncio.CancelledError:
            failure = FailureClass.CANCELLED_BY_USER if cancel_event.is_set() else FailureClass.STREAM_INTERRUPTED
            terminal = TerminalState.CANCELLED_BY_USER if cancel_event.is_set() else TerminalState.STREAM_INTERRUPTED
        except Exception:
            failure = FailureClass.UNKNOWN
            terminal = TerminalState.FAILED

        output = "".join(chunks)
        output_digest = "sha256:" + hashlib.sha256(output.encode("utf-8")).hexdigest()
        await self._runs.finalize(
            run_id,
            terminal,
            completed_at=datetime.now(UTC),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            output_digest=output_digest,
            failure_class=failure,
        )
        await self._events.append(
            run_id,
            "terminal",
            {
                "terminal_state": terminal.value,
                "failure_class": failure.value if failure is not None else None,
                "output_digest": output_digest,
            },
        )
        self._cancel_events.pop(run_id, None)

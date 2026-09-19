from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .contracts import GenerationConfig, RunEvent, SeatCreate, SeatRecord, TerminalState, ThreadCreate, ThreadRecord
from .models import RunEventModel, RunModel, SeatModel, ThreadModel


def _seat_record(row: SeatModel) -> SeatRecord:
    return SeatRecord(
        seat_id=row.seat_id,
        display_name=row.display_name,
        provider_id=row.provider_id,
        model_id=row.model_id,
        provider_family=row.provider_family,
        order_index=row.order_index,
        context_view_id=row.context_view_id,
        tool_policy_id=row.tool_policy_id,
        generation_config=GenerationConfig.model_validate(row.generation_config),
        independence_mode=row.independence_mode,
        visibility_policy=row.visibility_policy,
        schema_version=row.schema_version,
    )


class SeatRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def create(self, seat: SeatCreate) -> SeatRecord:
        row = SeatModel(
            seat_id=f"seat_{uuid4().hex}",
            **seat.model_dump(mode="json"),
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
        return _seat_record(row)

    async def list(self) -> list[SeatRecord]:
        async with self._sessions() as session:
            rows = (await session.scalars(select(SeatModel).order_by(SeatModel.order_index, SeatModel.seat_id))).all()
        return [_seat_record(row) for row in rows]

    async def get(self, seat_id: str) -> SeatRecord | None:
        async with self._sessions() as session:
            row = await session.get(SeatModel, seat_id)
        return _seat_record(row) if row else None

    async def update(self, seat_id: str, changes: dict[str, Any]) -> SeatRecord:
        allowed = set(SeatCreate.model_fields)
        if not set(changes) <= allowed:
            raise ValueError("unsupported seat field")
        async with self._sessions() as session:
            row = await session.get(SeatModel, seat_id)
            if row is None:
                raise KeyError(seat_id)
            for key, value in changes.items():
                if key == "generation_config" and isinstance(value, GenerationConfig):
                    value = value.model_dump(mode="json")
                setattr(row, key, value)
            await session.commit()
        return _seat_record(row)

    async def delete(self, seat_id: str) -> None:
        async with self._sessions() as session:
            result = await session.execute(delete(SeatModel).where(SeatModel.seat_id == seat_id))
            if result.rowcount == 0:
                raise KeyError(seat_id)
            await session.commit()


class RunRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def create(self, *, dispatch_id: str | None = None, **values: Any) -> RunModel:
        row = RunModel(
            run_id=f"run_{uuid4().hex}",
            dispatch_id=dispatch_id,
            started_at=datetime.now(UTC),
            **values,
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
        return row

    async def get(self, run_id: str) -> RunModel | None:
        async with self._sessions() as session:
            return await session.get(RunModel, run_id)

    async def finalize(self, run_id: str, terminal_state: TerminalState, *, completed_at: datetime, **changes: Any) -> RunModel:
        async with self._sessions() as session:
            row = await session.get(RunModel, run_id)
            if row is None:
                raise KeyError(run_id)
            if row.terminal_state is not None:
                raise ValueError(f"run {run_id} already terminal: {row.terminal_state}")
            row.terminal_state = terminal_state.value
            row.completed_at = completed_at
            for key, value in changes.items():
                if not hasattr(row, key):
                    raise ValueError(f"unsupported run field: {key}")
                setattr(row, key, value.value if hasattr(value, "value") else value)
            await session.commit()
        return row

    async def mark_first_token(self, run_id: str, at: datetime) -> None:
        async with self._sessions() as session:
            row = await session.get(RunModel, run_id)
            if row is None:
                raise KeyError(run_id)
            if row.first_token_at is None:
                row.first_token_at = at
                await session.commit()


class EventRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def append(self, run_id: str, event_type: str, data: dict[str, Any]) -> RunEvent:
        async with self._sessions() as session:
            max_sequence = await session.scalar(
                select(func.max(RunEventModel.sequence)).where(RunEventModel.run_id == run_id)
            )
            row = RunEventModel(
                run_id=run_id,
                sequence=(max_sequence or 0) + 1,
                event_type=event_type,
                created_at=datetime.now(UTC),
                data=data,
            )
            session.add(row)
            await session.commit()
        return RunEvent(
            run_id=row.run_id,
            sequence=row.sequence,
            event_type=row.event_type,
            created_at=row.created_at,
            data=row.data,
        )

    async def list_after(self, run_id: str, sequence: int) -> list[RunEvent]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(RunEventModel)
                    .where(RunEventModel.run_id == run_id, RunEventModel.sequence > sequence)
                    .order_by(RunEventModel.sequence)
                )
            ).all()
        return [
            RunEvent(
                run_id=row.run_id,
                sequence=row.sequence,
                event_type=row.event_type,
                created_at=row.created_at,
                data=row.data,
            )
            for row in rows
        ]


def _thread_record(
    row: ThreadModel,
    *,
    run_count: int = 0,
    last_run_at: datetime | None = None,
) -> ThreadRecord:
    return ThreadRecord(
        thread_id=row.thread_id,
        title=row.title,
        created_at=row.created_at,
        run_count=run_count,
        last_run_at=last_run_at,
        schema_version=row.schema_version,
    )


class ThreadRepository:
    """Thread listing over explicit thread rows plus implicit threads derived from runs.

    `runs.thread_id` carries no foreign key in the live schema, so historical runs
    (for example `thread_local_default`) can reference a thread that has no row.
    The listing therefore unions explicit thread rows with the distinct thread_ids
    observed in runs, so no run is ever invisible. Reads never rewrite a run and
    never backfill implicitly; nothing is hidden or renamed.
    """

    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def create(self, payload: ThreadCreate) -> ThreadRecord:
        row = ThreadModel(
            thread_id=f"thread_{uuid4().hex}",
            title=payload.title,
            created_at=datetime.now(UTC),
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
        return _thread_record(row)

    async def _activity(self, session: AsyncSession, thread_id: str) -> tuple[int, Any]:
        count, last = (
            await session.execute(
                select(func.count(RunModel.run_id), func.max(RunModel.started_at)).where(
                    RunModel.thread_id == thread_id
                )
            )
        ).one()
        return int(count or 0), last

    async def get(self, thread_id: str) -> ThreadRecord | None:
        async with self._sessions() as session:
            row = await session.get(ThreadModel, thread_id)
            count, last = await self._activity(session, thread_id)
        if row is not None:
            return _thread_record(row, run_count=count, last_run_at=last)
        if count == 0:
            return None
        return ThreadRecord(
            thread_id=thread_id,
            title=None,
            created_at=last or datetime.now(UTC),
            run_count=count,
            last_run_at=last,
            schema_version=1,
        )

    async def list(self) -> list[ThreadRecord]:
        async with self._sessions() as session:
            explicit = (await session.scalars(select(ThreadModel))).all()
            activity_rows = (
                await session.execute(
                    select(
                        RunModel.thread_id,
                        func.count(RunModel.run_id),
                        func.max(RunModel.started_at),
                    ).group_by(RunModel.thread_id)
                )
            ).all()
        activity = {row[0]: (int(row[1] or 0), row[2]) for row in activity_rows}
        records: list[ThreadRecord] = []
        for row in explicit:
            count, last = activity.get(row.thread_id, (0, None))
            records.append(_thread_record(row, run_count=count, last_run_at=last))
        known = {row.thread_id for row in explicit}
        for thread_id, (count, last) in activity.items():
            if thread_id in known:
                continue
            records.append(
                ThreadRecord(
                    thread_id=thread_id,
                    title=None,
                    created_at=last or datetime.now(UTC),
                    run_count=count,
                    last_run_at=last,
                    schema_version=1,
                )
            )

        def _sort_key(item: ThreadRecord) -> tuple[str, str]:
            # str() keeps the key comparable even if SQLite returns naive stamps
            # for some rows and timezone-aware ones for others.
            return (str(item.last_run_at or item.created_at), item.thread_id)

        records.sort(key=_sort_key, reverse=True)
        return records

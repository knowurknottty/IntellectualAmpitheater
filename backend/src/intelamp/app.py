from __future__ import annotations

from collections.abc import Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .config import DEFAULT_DATABASE_URL, DEFAULT_PROVIDERS_PATH, build_registry, load_provider_definitions
from .contracts import ProviderDefinition
from .database import Base, create_engine_and_session
from .dispatch import DispatchEngine
from .providers.base import ProviderAdapter
from .routes import RouteServices, create_router
from .repositories import EventRepository, RunRepository, SeatRepository, ThreadRepository


def create_app(
    *,
    database_url: str = DEFAULT_DATABASE_URL,
    provider_definitions: list[ProviderDefinition] | None = None,
    providers_path: str | Path = DEFAULT_PROVIDERS_PATH,
    adapters: Mapping[str, ProviderAdapter] | None = None,
    initialize_schema: bool = False,
) -> FastAPI:
    definitions = provider_definitions if provider_definitions is not None else load_provider_definitions(providers_path)
    engine, sessions = create_engine_and_session(database_url)
    registry = build_registry(definitions, adapters=adapters)
    seats = SeatRepository(sessions)
    runs = RunRepository(sessions)
    events = EventRepository(sessions)
    threads = ThreadRepository(sessions)
    dispatch = DispatchEngine(seats=seats, runs=runs, events=events, registry=registry)
    services = RouteServices(seats=seats, runs=runs, events=events, threads=threads, registry=registry, dispatch=dispatch)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if initialize_schema:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        try:
            yield
        finally:
            closed: set[int] = set()
            for definition in registry.definitions():
                registered = registry.get(definition.provider_id)
                adapter = registered.adapter
                if adapter is None or id(adapter) in closed:
                    continue
                closed.add(id(adapter))
                aclose = getattr(adapter, "aclose", None)
                if aclose is not None:
                    await aclose()
            await engine.dispose()

    app = FastAPI(title="IntelAMP Gateway", version="0.1.0", lifespan=lifespan)
    app.state.services = services
    app.state.database_engine = engine
    app.include_router(create_router(services))
    return app


def create_app_from_env() -> FastAPI:
    return create_app()

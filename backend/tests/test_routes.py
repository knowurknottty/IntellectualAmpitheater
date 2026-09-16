import asyncio
import json

import httpx
import pytest

from intelamp.app import create_app
from intelamp.config import build_registry, load_provider_definitions
from intelamp.contracts import CapabilityState, FailureClass, ProviderCapabilities, ProviderDefinition
from intelamp.providers.base import ProviderStreamEvent, ProviderStreamEventType
from intelamp.providers.openai_compat import ProviderAdapterError


class ApiAdapter:
    def __init__(self, chunks=("hello",), *, delay=0.01):
        self.chunks = list(chunks)
        self.delay = delay
        self.calls = 0

    async def list_models(self):
        return ["test-model"]

    async def stream_chat(self, request, cancel_event):
        self.calls += 1
        for chunk in self.chunks:
            await asyncio.sleep(self.delay)
            if cancel_event.is_set():
                raise ProviderAdapterError(FailureClass.CANCELLED_BY_USER, "cancelled")
            yield ProviderStreamEvent(event_type=ProviderStreamEventType.DELTA, data={"text": chunk})
        yield ProviderStreamEvent(event_type=ProviderStreamEventType.USAGE, data={"prompt_tokens": 2, "completion_tokens": len(self.chunks)})
        yield ProviderStreamEvent(event_type=ProviderStreamEventType.DONE, data={})


def provider(*, credential_env: str | None = "INTELAMP_TEST_SECRET") -> ProviderDefinition:
    return ProviderDefinition(
        provider_id="test-provider",
        display_name="Test Provider",
        adapter="openai_compat",
        base_url="http://provider.test/v1",
        provider_family="test",
        credential_env=credential_env,
        max_concurrent_requests=1,
        capabilities=ProviderCapabilities(
            streaming=CapabilityState.SUPPORTED,
            temperature=CapabilityState.SUPPORTED,
            cancellation=CapabilityState.SUPPORTED,
        ),
    )


async def make_client(tmp_path, adapter=None):
    adapter = adapter or ApiAdapter()
    app = create_app(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'api.sqlite3'}",
        provider_definitions=[provider()],
        adapters={"test-provider": adapter},
        initialize_schema=True,
    )
    lifespan = app.router.lifespan_context(app)
    await lifespan.__aenter__()
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
    return app, client, lifespan, adapter


async def close_client(client, lifespan):
    await client.aclose()
    await lifespan.__aexit__(None, None, None)


async def create_seat(client, name="Seat", provider_id="test-provider", model_id="test-model"):
    response = await client.post(
        "/api/seats",
        json={"display_name": name, "provider_id": provider_id, "model_id": model_id},
    )
    assert response.status_code == 201, response.text
    return response.json()


def sse_ids(text: str) -> list[int]:
    return [int(line[3:].strip()) for line in text.splitlines() if line.startswith("id:")]


@pytest.mark.asyncio
async def test_health_and_seat_crud(tmp_path):
    app, client, lifespan, _ = await make_client(tmp_path)
    try:
        assert (await client.get("/api/health")).json() == {"status": "ok"}
        seat = await create_seat(client, "Alpha")
        listed = (await client.get("/api/seats")).json()["seats"]
        assert [item["seat_id"] for item in listed] == [seat["seat_id"]]
        patched = await client.patch(f"/api/seats/{seat['seat_id']}", json={"display_name": "Beta"})
        assert patched.status_code == 200
        assert patched.json()["display_name"] == "Beta"
        deleted = await client.delete(f"/api/seats/{seat['seat_id']}")
        assert deleted.status_code == 204
        assert (await client.get("/api/seats")).json()["seats"] == []
    finally:
        await close_client(client, lifespan)


@pytest.mark.asyncio
async def test_provider_api_surfaces_capabilities_but_never_credential_config(tmp_path, monkeypatch):
    monkeypatch.setenv("INTELAMP_TEST_SECRET", "do-not-return-me")
    app, client, lifespan, _ = await make_client(tmp_path)
    try:
        response = await client.get("/api/providers")
        assert response.status_code == 200
        body = response.json()
        item = body["providers"][0]
        assert item["provider_id"] == "test-provider"
        assert item["capabilities"]["streaming"] == "supported"
        serialized = json.dumps(body)
        assert "credential_env" not in serialized
        assert "INTELAMP_TEST_SECRET" not in serialized
        assert "do-not-return-me" not in serialized
    finally:
        await close_client(client, lifespan)


@pytest.mark.asyncio
async def test_dispatch_sse_sequence_ids_resume_and_receipt(tmp_path):
    app, client, lifespan, _ = await make_client(tmp_path)
    try:
        seat = await create_seat(client)
        dispatched = await client.post(
            "/api/dispatch",
            json={"thread_id": "thread-1", "prompt": "hello", "seat_ids": [seat["seat_id"]]},
        )
        assert dispatched.status_code == 202
        run_id = dispatched.json()["run_ids"][0]

        stream = await client.get(f"/api/runs/{run_id}/events")
        assert stream.status_code == 200
        ids = sse_ids(stream.text)
        assert ids == sorted(ids)
        assert ids[0] == 1
        assert len(ids) >= 4
        assert f"id: {ids[-1]}" in stream.text

        resumed = await client.get(f"/api/runs/{run_id}/events", headers={"Last-Event-ID": "2"})
        resumed_ids = sse_ids(resumed.text)
        assert resumed_ids
        assert min(resumed_ids) > 2

        receipt = await client.get(f"/api/runs/{run_id}/receipt")
        assert receipt.status_code == 200
        assert receipt.json()["run_id"] == run_id
        assert receipt.json()["terminal_state"] == "completed"
        assert receipt.json()["provider_id"] == "test-provider"
    finally:
        await close_client(client, lifespan)


@pytest.mark.asyncio
async def test_dispatch_rejects_unknown_seat_with_typed_404(tmp_path):
    app, client, lifespan, _ = await make_client(tmp_path)
    try:
        response = await client.post(
            "/api/dispatch",
            json={"thread_id": "thread-1", "prompt": "hello", "seat_ids": ["seat_missing"]},
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "seat_not_found"
    finally:
        await close_client(client, lifespan)


@pytest.mark.asyncio
async def test_cancel_route_reaches_terminal_cancelled_receipt(tmp_path):
    slow = ApiAdapter(chunks=("one", "two", "three", "four"), delay=0.05)
    app, client, lifespan, _ = await make_client(tmp_path, slow)
    try:
        seat = await create_seat(client)
        dispatched = await client.post(
            "/api/dispatch",
            json={"thread_id": "thread-1", "prompt": "hello", "seat_ids": [seat["seat_id"]]},
        )
        run_id = dispatched.json()["run_ids"][0]
        await asyncio.sleep(0.07)
        cancel = await client.post(f"/api/runs/{run_id}/cancel")
        assert cancel.status_code == 202
        assert cancel.json() == {"run_id": run_id, "cancel_requested": True}
        stream = await client.get(f"/api/runs/{run_id}/events")
        assert "cancelled_by_user" in stream.text
        receipt = await client.get(f"/api/runs/{run_id}/receipt")
        assert receipt.status_code == 200
        assert receipt.json()["terminal_state"] == "cancelled_by_user"
    finally:
        await close_client(client, lifespan)


@pytest.mark.asyncio
async def test_missing_run_endpoints_return_typed_404(tmp_path):
    app, client, lifespan, _ = await make_client(tmp_path)
    try:
        for method, path in [
            (client.get, "/api/runs/run_missing/receipt"),
            (client.get, "/api/runs/run_missing/events"),
            (client.post, "/api/runs/run_missing/cancel"),
        ]:
            response = await method(path)
            assert response.status_code == 404
            assert response.json()["error"]["code"] == "run_not_found"
    finally:
        await close_client(client, lifespan)


def test_provider_toml_loader_and_server_side_credential_resolution(tmp_path, monkeypatch):
    config_path = tmp_path / "providers.toml"
    config_path.write_text(
        """
[[providers]]
provider_id = "p"
display_name = "Provider"
adapter = "openai_compat"
base_url = "http://provider.test/v1"
credential_env = "INTELAMP_FAKE_KEY"
max_concurrent_requests = 1
""".strip()
    )
    monkeypatch.setenv("INTELAMP_FAKE_KEY", "fake-secret")
    definitions = load_provider_definitions(config_path)
    registry = build_registry(definitions)
    registered = registry.get("p")
    assert registered.definition.credential_env == "INTELAMP_FAKE_KEY"
    assert registered.adapter is not None
    assert getattr(registered.adapter, "_credential") == "fake-secret"

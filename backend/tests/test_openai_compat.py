import httpx
import pytest

from intelamp.contracts import FailureClass, ProviderDefinition
from intelamp.providers.base import ProviderStreamEventType
from intelamp.providers.openai_compat import OpenAICompatibleAdapter, ProviderAdapterError


SSE_OK = """data: {\"choices\":[{\"delta\":{\"role\":\"assistant\"}}]}\n\ndata: {\"choices\":[{\"delta\":{\"content\":\"hello \"}}]}\n\ndata: {\"choices\":[{\"delta\":{\"content\":\"world\"}}]}\n\ndata: {\"choices\":[],\"usage\":{\"prompt_tokens\":3,\"completion_tokens\":2,\"total_tokens\":5}}\n\ndata: [DONE]\n\n"""
SSE_MALFORMED = "data: {not-json}\n\n"


def definition() -> ProviderDefinition:
    return ProviderDefinition(
        provider_id="test-openai",
        display_name="Test OpenAI-compatible",
        adapter="openai_compat",
        base_url="http://provider.test/v1",
        max_concurrent_requests=1,
    )


def adapter_for(*, body: str = SSE_OK, status: int = 200, error=None, credential=None, seen=None):
    async def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        if error is not None:
            raise error(request)
        return httpx.Response(status, text=body, request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OpenAICompatibleAdapter(definition(), credential=credential, client=client)
    return adapter, client


async def collect(adapter: OpenAICompatibleAdapter):
    cancel = __import__("asyncio").Event()
    return [event async for event in adapter.stream_chat({"model": "m", "messages": [{"role": "user", "content": "hi"}]}, cancel)]


@pytest.mark.asyncio
async def test_stream_parser_emits_delta_usage_and_done_from_recorded_sse_fixture():
    adapter, client = adapter_for()
    try:
        events = await collect(adapter)
    finally:
        await client.aclose()

    assert [event.event_type for event in events] == [
        ProviderStreamEventType.DELTA,
        ProviderStreamEventType.DELTA,
        ProviderStreamEventType.USAGE,
        ProviderStreamEventType.DONE,
    ]
    assert "".join(event.data["text"] for event in events if event.event_type is ProviderStreamEventType.DELTA) == "hello world"
    usage = next(event.data for event in events if event.event_type is ProviderStreamEventType.USAGE)
    assert usage == {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}


@pytest.mark.asyncio
async def test_done_marker_is_required_so_truncated_stream_is_interrupted():
    body = 'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n'
    adapter, client = adapter_for(body=body)
    try:
        with pytest.raises(ProviderAdapterError) as exc:
            await collect(adapter)
    finally:
        await client.aclose()

    assert exc.value.failure_class is FailureClass.STREAM_INTERRUPTED


@pytest.mark.asyncio
async def test_malformed_json_maps_to_protocol_error():
    adapter, client = adapter_for(body=SSE_MALFORMED)
    try:
        with pytest.raises(ProviderAdapterError) as exc:
            await collect(adapter)
    finally:
        await client.aclose()

    assert exc.value.failure_class is FailureClass.PROVIDER_PROTOCOL_ERROR


@pytest.mark.asyncio
async def test_http_429_maps_to_rate_limit():
    adapter, client = adapter_for(status=429, body="rate limited")
    try:
        with pytest.raises(ProviderAdapterError) as exc:
            await collect(adapter)
    finally:
        await client.aclose()

    assert exc.value.failure_class is FailureClass.PROVIDER_RATE_LIMITED
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_timeout_maps_to_provider_timeout():
    adapter, client = adapter_for(error=lambda request: httpx.ReadTimeout("late", request=request))
    try:
        with pytest.raises(ProviderAdapterError) as exc:
            await collect(adapter)
    finally:
        await client.aclose()

    assert exc.value.failure_class is FailureClass.PROVIDER_TIMEOUT


@pytest.mark.asyncio
async def test_other_non_2xx_maps_to_protocol_error():
    adapter, client = adapter_for(status=502, body="bad gateway")
    try:
        with pytest.raises(ProviderAdapterError) as exc:
            await collect(adapter)
    finally:
        await client.aclose()

    assert exc.value.failure_class is FailureClass.PROVIDER_PROTOCOL_ERROR
    assert exc.value.status_code == 502


@pytest.mark.asyncio
async def test_list_models_and_bearer_header_are_server_side_only_when_supplied():
    seen = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [{"id": "model-a"}, {"id": "model-b"}]}, request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OpenAICompatibleAdapter(definition(), client=client)
    try:
        assert await adapter.list_models() == ["model-a", "model-b"]
    finally:
        await client.aclose()
    assert "authorization" not in seen[0].headers

    seen.clear()
    client2 = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter2 = OpenAICompatibleAdapter(definition(), credential="server-secret", client=client2)
    try:
        assert await adapter2.list_models() == ["model-a", "model-b"]
    finally:
        await client2.aclose()
    assert seen[0].headers["authorization"] == "Bearer server-secret"

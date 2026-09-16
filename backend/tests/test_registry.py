import asyncio

import pytest

from intelamp.contracts import CapabilityState, ProviderCapabilities, ProviderDefinition
from intelamp.registry import ProviderRegistry


def provider(provider_id: str, *, max_concurrent_requests: int = 1) -> ProviderDefinition:
    return ProviderDefinition(
        provider_id=provider_id,
        display_name=provider_id,
        adapter="openai_compat",
        base_url="http://127.0.0.1:8080/v1",
        provider_family="local",
        max_concurrent_requests=max_concurrent_requests,
        capabilities=ProviderCapabilities(streaming=CapabilityState.SUPPORTED),
    )


def test_registry_get_is_stable_and_owns_per_provider_semaphore():
    registry = ProviderRegistry([provider("llama", max_concurrent_requests=2), provider("other")])

    llama = registry.get("llama")
    other = registry.get("other")

    assert registry.get("llama") is llama
    assert isinstance(llama.semaphore, asyncio.Semaphore)
    assert llama.max_concurrent_requests == 2
    assert other.semaphore is not llama.semaphore
    assert llama.definition.provider_id == "llama"


def test_registry_rejects_duplicate_provider_ids():
    with pytest.raises(ValueError, match="duplicate provider_id"):
        ProviderRegistry([provider("same"), provider("same")])


def test_registry_rejects_zero_concurrency_even_from_unvalidated_mapping():
    raw = {
        "provider_id": "broken",
        "display_name": "Broken",
        "adapter": "openai_compat",
        "base_url": "http://127.0.0.1:8080/v1",
        "max_concurrent_requests": 0,
    }

    with pytest.raises(ValueError, match="max_concurrent_requests"):
        ProviderRegistry([raw])


def test_registry_missing_provider_is_key_error():
    registry = ProviderRegistry([provider("llama")])

    with pytest.raises(KeyError, match="missing"):
        registry.get("missing")

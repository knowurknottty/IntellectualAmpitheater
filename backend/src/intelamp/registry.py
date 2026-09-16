from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .contracts import ProviderDefinition
from .providers.base import ProviderAdapter


@dataclass(slots=True)
class RegisteredProvider:
    definition: ProviderDefinition
    semaphore: asyncio.Semaphore
    adapter: ProviderAdapter | None = None

    @property
    def max_concurrent_requests(self) -> int:
        return self.definition.max_concurrent_requests


class ProviderRegistry:
    def __init__(
        self,
        providers: Iterable[ProviderDefinition | Mapping[str, Any]] = (),
        *,
        adapters: Mapping[str, ProviderAdapter] | None = None,
    ) -> None:
        self._providers: dict[str, RegisteredProvider] = {}
        adapters = adapters or {}
        for candidate in providers:
            try:
                definition = ProviderDefinition.model_validate(candidate)
            except ValidationError as exc:
                raise ValueError(f"invalid provider definition: {exc}") from exc

            provider_id = definition.provider_id
            if provider_id in self._providers:
                raise ValueError(f"duplicate provider_id: {provider_id}")
            self._providers[provider_id] = RegisteredProvider(
                definition=definition,
                semaphore=asyncio.Semaphore(definition.max_concurrent_requests),
                adapter=adapters.get(provider_id),
            )

    def get(self, provider_id: str) -> RegisteredProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise KeyError(f"provider_id not registered: {provider_id}") from exc

    def definitions(self) -> list[ProviderDefinition]:
        return [registered.definition for registered in self._providers.values()]

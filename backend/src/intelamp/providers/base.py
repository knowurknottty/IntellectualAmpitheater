from __future__ import annotations

import asyncio
from enum import StrEnum
from typing import Any, AsyncIterator, Protocol

from ..contracts import StrictModel


class ProviderStreamEventType(StrEnum):
    DELTA = "delta"
    USAGE = "usage"
    DONE = "done"
    ERROR = "error"


class ProviderStreamEvent(StrictModel):
    event_type: ProviderStreamEventType
    data: dict[str, Any]


class ProviderAdapter(Protocol):
    async def list_models(self) -> list[str]: ...

    def stream_chat(
        self,
        request: Any,
        cancel_event: asyncio.Event,
    ) -> AsyncIterator[ProviderStreamEvent]: ...

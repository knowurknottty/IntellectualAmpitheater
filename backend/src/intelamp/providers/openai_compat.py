from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from typing import Any

import httpx

from ..contracts import FailureClass, ProviderDefinition
from .base import ProviderStreamEvent, ProviderStreamEventType


class ProviderAdapterError(RuntimeError):
    def __init__(
        self,
        failure_class: FailureClass,
        message: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_class = failure_class
        self.status_code = status_code


class OpenAICompatibleAdapter:
    def __init__(
        self,
        definition: ProviderDefinition,
        *,
        credential: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: httpx.Timeout | float = 60.0,
    ) -> None:
        self.definition = definition
        self._credential = credential
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)

    def _url(self, path: str) -> str:
        return f"{self.definition.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _headers(self) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if self._credential:
            headers["authorization"] = f"Bearer {self._credential}"
        return headers

    @staticmethod
    def _status_error(status_code: int) -> ProviderAdapterError:
        if status_code == 429:
            return ProviderAdapterError(
                FailureClass.PROVIDER_RATE_LIMITED,
                "provider returned HTTP 429",
                status_code=status_code,
            )
        return ProviderAdapterError(
            FailureClass.PROVIDER_PROTOCOL_ERROR,
            f"provider returned HTTP {status_code}",
            status_code=status_code,
        )

    async def list_models(self) -> list[str]:
        try:
            response = await self._client.get(self._url("models"), headers=self._headers())
        except httpx.TimeoutException as exc:
            raise ProviderAdapterError(FailureClass.PROVIDER_TIMEOUT, "provider model listing timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderAdapterError(FailureClass.PROVIDER_UNAVAILABLE, "provider model listing failed") from exc

        if not 200 <= response.status_code < 300:
            raise self._status_error(response.status_code)
        try:
            payload = response.json()
            rows = payload["data"]
            models = [row["id"] for row in rows if isinstance(row, Mapping) and isinstance(row.get("id"), str)]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ProviderAdapterError(
                FailureClass.PROVIDER_PROTOCOL_ERROR,
                "provider model listing response was not OpenAI-compatible JSON",
            ) from exc
        return models

    async def stream_chat(
        self,
        request: Mapping[str, Any],
        cancel_event: asyncio.Event,
    ) -> AsyncIterator[ProviderStreamEvent]:
        if cancel_event.is_set():
            raise ProviderAdapterError(FailureClass.CANCELLED_BY_USER, "request cancelled before dispatch")

        payload = dict(request)
        payload["stream"] = True
        saw_done = False

        try:
            async with self._client.stream(
                "POST",
                self._url("chat/completions"),
                headers=self._headers(),
                json=payload,
            ) as response:
                if not 200 <= response.status_code < 300:
                    raise self._status_error(response.status_code)

                async for line in response.aiter_lines():
                    if cancel_event.is_set():
                        await response.aclose()
                        raise ProviderAdapterError(FailureClass.CANCELLED_BY_USER, "request cancelled by user")
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    if not line.startswith("data:"):
                        continue

                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        saw_done = True
                        yield ProviderStreamEvent(event_type=ProviderStreamEventType.DONE, data={})
                        break
                    try:
                        item = json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise ProviderAdapterError(
                            FailureClass.PROVIDER_PROTOCOL_ERROR,
                            "provider emitted malformed SSE JSON",
                        ) from exc
                    if not isinstance(item, Mapping):
                        raise ProviderAdapterError(
                            FailureClass.PROVIDER_PROTOCOL_ERROR,
                            "provider emitted non-object SSE JSON",
                        )

                    usage = item.get("usage")
                    if isinstance(usage, Mapping):
                        yield ProviderStreamEvent(
                            event_type=ProviderStreamEventType.USAGE,
                            data=dict(usage),
                        )

                    choices = item.get("choices", [])
                    if isinstance(choices, list):
                        for choice in choices:
                            if not isinstance(choice, Mapping):
                                continue
                            delta = choice.get("delta")
                            if not isinstance(delta, Mapping):
                                continue
                            content = delta.get("content")
                            if isinstance(content, str) and content:
                                yield ProviderStreamEvent(
                                    event_type=ProviderStreamEventType.DELTA,
                                    data={"text": content},
                                )
        except ProviderAdapterError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderAdapterError(FailureClass.PROVIDER_TIMEOUT, "provider stream timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderAdapterError(FailureClass.PROVIDER_UNAVAILABLE, "provider stream failed") from exc

        if not saw_done:
            raise ProviderAdapterError(
                FailureClass.STREAM_INTERRUPTED,
                "provider stream ended without an OpenAI [DONE] marker",
            )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Mapping

from .contracts import ProviderDefinition
from .providers.base import ProviderAdapter
from .providers.openai_compat import OpenAICompatibleAdapter
from .registry import ProviderRegistry


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROVIDERS_PATH = REPO_ROOT / "config" / "providers.example.toml"
DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{REPO_ROOT / 'intelamp.sqlite3'}"


def load_provider_definitions(path: str | Path) -> list[ProviderDefinition]:
    config_path = Path(path)
    data = tomllib.loads(config_path.read_text())
    rows = data.get("providers", [])
    if not isinstance(rows, list):
        raise ValueError("providers TOML must contain [[providers]] entries")
    return [ProviderDefinition.model_validate(row) for row in rows]


def build_registry(
    definitions: list[ProviderDefinition],
    *,
    adapters: Mapping[str, ProviderAdapter] | None = None,
) -> ProviderRegistry:
    overrides = dict(adapters or {})
    resolved: dict[str, ProviderAdapter] = dict(overrides)
    for definition in definitions:
        if definition.provider_id in resolved:
            continue
        if definition.adapter == "openai_compat":
            credential = os.environ.get(definition.credential_env) if definition.credential_env else None
            resolved[definition.provider_id] = OpenAICompatibleAdapter(
                definition,
                credential=credential,
            )
    return ProviderRegistry(definitions, adapters=resolved)

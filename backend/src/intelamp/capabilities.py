from __future__ import annotations

from pydantic import Field

from .contracts import (
    CapabilityState,
    ProviderCapabilities,
    RequestedCapabilities,
    StrictModel,
)


class CapabilityIssue(StrictModel):
    capability: str
    state: CapabilityState
    message: str


class CapabilityCompileResult(StrictModel):
    states: dict[str, CapabilityState] = Field(default_factory=dict)
    hard_incompatibilities: list[CapabilityIssue] = Field(default_factory=list)
    warnings: list[CapabilityIssue] = Field(default_factory=list)

    @property
    def compatible(self) -> bool:
        return not self.hard_incompatibilities


def _offered_state(name: str, offered: ProviderCapabilities) -> CapabilityState:
    if name not in ProviderCapabilities.model_fields:
        return CapabilityState.UNKNOWN
    value = getattr(offered, name)
    return value if isinstance(value, CapabilityState) else CapabilityState(value)


def compile_capabilities(
    requested: RequestedCapabilities,
    offered: ProviderCapabilities,
) -> CapabilityCompileResult:
    states: dict[str, CapabilityState] = {}
    hard: list[CapabilityIssue] = []
    warnings: list[CapabilityIssue] = []

    names = sorted(requested.required | requested.optional)
    for name in names:
        state = _offered_state(name, offered)
        states[name] = state
        if state is CapabilityState.SUPPORTED:
            continue

        issue = CapabilityIssue(
            capability=name,
            state=state,
            message=f"{name} requested but provider capability state is {state.value}",
        )
        if name in requested.required:
            hard.append(issue)
        else:
            warnings.append(issue)

    return CapabilityCompileResult(
        states=states,
        hard_incompatibilities=hard,
        warnings=warnings,
    )

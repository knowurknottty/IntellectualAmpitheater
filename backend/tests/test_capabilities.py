from intelamp.capabilities import compile_capabilities
from intelamp.contracts import CapabilityState, ProviderCapabilities, RequestedCapabilities


def test_supported_controls_map_without_issues():
    requested = RequestedCapabilities(required={"streaming"}, optional={"temperature"})
    offered = ProviderCapabilities(
        streaming=CapabilityState.SUPPORTED,
        temperature=CapabilityState.SUPPORTED,
    )

    result = compile_capabilities(requested, offered)

    assert result.states == {
        "streaming": CapabilityState.SUPPORTED,
        "temperature": CapabilityState.SUPPORTED,
    }
    assert result.hard_incompatibilities == []
    assert result.warnings == []
    assert result.compatible is True


def test_required_unsupported_control_is_hard_incompatibility():
    requested = RequestedCapabilities(required={"tool_calling"})
    offered = ProviderCapabilities(tool_calling=CapabilityState.UNSUPPORTED)

    result = compile_capabilities(requested, offered)

    assert result.compatible is False
    assert [(issue.capability, issue.state) for issue in result.hard_incompatibilities] == [
        ("tool_calling", CapabilityState.UNSUPPORTED)
    ]
    assert result.warnings == []


def test_optional_uncontrolled_or_unsupported_controls_are_warnings():
    requested = RequestedCapabilities(optional={"seed", "web_search"})
    offered = ProviderCapabilities(
        seed=CapabilityState.PROVIDER_DEFAULT,
        web_search=CapabilityState.UNSUPPORTED,
    )

    result = compile_capabilities(requested, offered)

    assert result.compatible is True
    assert result.hard_incompatibilities == []
    assert {(issue.capability, issue.state) for issue in result.warnings} == {
        ("seed", CapabilityState.PROVIDER_DEFAULT),
        ("web_search", CapabilityState.UNSUPPORTED),
    }


def test_unknown_control_never_becomes_supported():
    requested = RequestedCapabilities(required={"future_control"}, optional={"citations"})
    offered = ProviderCapabilities(citations=CapabilityState.UNKNOWN)

    result = compile_capabilities(requested, offered)

    assert result.states["future_control"] is CapabilityState.UNKNOWN
    assert result.states["citations"] is CapabilityState.UNKNOWN
    assert result.compatible is False
    assert result.hard_incompatibilities[0].capability == "future_control"
    assert result.warnings[0].capability == "citations"

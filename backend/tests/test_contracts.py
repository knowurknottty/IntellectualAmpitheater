from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from intelamp.contracts import (
    CapabilityState,
    FailureClass,
    ProviderCapabilities,
    RunReceipt,
    TerminalState,
)


def test_capability_state_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        CapabilityState("maybe")


def test_provider_capabilities_forbid_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProviderCapabilities(streaming="supported", made_up="supported")


def test_receipt_unknown_usage_stays_none_and_round_trips_digests() -> None:
    now = datetime.now(UTC)
    receipt = RunReceipt(
        run_id="run_1",
        thread_id="thread_1",
        turn_parent=None,
        seat_id="seat_1",
        provider_id="local-llama",
        model_id="qwen-local",
        provider_family="qwen",
        request_digest="sha256:req",
        context_view_digest="sha256:ctx",
        evidence_root_digest="sha256:evidence",
        tool_policy_digest="sha256:tools",
        started_at=now,
        first_token_at=None,
        completed_at=None,
        terminal_state="stream_interrupted",
        output_digest=None,
    )
    assert receipt.input_tokens is None
    assert receipt.output_tokens is None
    assert receipt.estimated_cost is None
    restored = RunReceipt.model_validate_json(receipt.model_dump_json())
    assert restored.request_digest == "sha256:req"
    assert restored.context_view_digest == "sha256:ctx"
    assert restored.evidence_root_digest == "sha256:evidence"
    assert restored.tool_policy_digest == "sha256:tools"


def test_terminal_and_failure_enums_reject_unknown_values() -> None:
    with pytest.raises(ValueError):
        TerminalState("magically_done")
    with pytest.raises(ValueError):
        FailureClass("mystery_provider_thing")

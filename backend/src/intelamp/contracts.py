from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CapabilityState(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    PROVIDER_DEFAULT = "provider_default"
    UNKNOWN = "unknown"


class FailureClass(StrEnum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_RATE_LIMITED = "provider_rate_limited"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_PROTOCOL_ERROR = "provider_protocol_error"
    CONTEXT_TOO_LARGE = "context_too_large"
    CAPABILITY_MISMATCH = "capability_mismatch"
    CANCELLED_BY_USER = "cancelled_by_user"
    TOOL_PLAN_REFUSED = "tool_plan_refused"
    TOOL_EXECUTION_FAILED = "tool_execution_failed"
    CAPT_AUTHORITY_REFUSED = "capt_authority_refused"
    CAPT_APPROVAL_REQUIRED = "capt_approval_required"
    STORAGE_ERROR = "storage_error"
    STREAM_INTERRUPTED = "stream_interrupted"
    UNKNOWN = "unknown"


class TerminalState(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED_BY_USER = "cancelled_by_user"
    STREAM_INTERRUPTED = "stream_interrupted"
    INDETERMINATE = "indeterminate"


class ProviderCapabilities(StrictModel):
    streaming: CapabilityState = CapabilityState.UNKNOWN
    system_messages: CapabilityState = CapabilityState.UNKNOWN
    multimodal_input: CapabilityState = CapabilityState.UNKNOWN
    image_output: CapabilityState = CapabilityState.UNKNOWN
    tool_calling: CapabilityState = CapabilityState.UNKNOWN
    parallel_tool_calls: CapabilityState = CapabilityState.UNKNOWN
    structured_output: CapabilityState = CapabilityState.UNKNOWN
    reasoning_control: CapabilityState = CapabilityState.UNKNOWN
    temperature: CapabilityState = CapabilityState.UNKNOWN
    top_p: CapabilityState = CapabilityState.UNKNOWN
    seed: CapabilityState = CapabilityState.UNKNOWN
    max_output_tokens: CapabilityState = CapabilityState.UNKNOWN
    citations: CapabilityState = CapabilityState.UNKNOWN
    web_search: CapabilityState = CapabilityState.UNKNOWN
    file_upload: CapabilityState = CapabilityState.UNKNOWN
    native_memory: CapabilityState = CapabilityState.UNKNOWN
    context_window: CapabilityState = CapabilityState.UNKNOWN
    usage_reporting: CapabilityState = CapabilityState.UNKNOWN
    cancellation: CapabilityState = CapabilityState.UNKNOWN


class ProviderDefinition(StrictModel):
    provider_id: str
    display_name: str
    adapter: str
    base_url: str
    provider_family: str | None = None
    credential_env: str | None = None
    max_concurrent_requests: int = Field(default=1, ge=1)
    capabilities: ProviderCapabilities = Field(default_factory=ProviderCapabilities)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationConfig(StrictModel):
    temperature: float | None = None
    top_p: float | None = None
    seed: int | None = None
    max_output_tokens: int | None = Field(default=None, ge=1)
    reasoning_control: str | None = None


class SeatCreate(StrictModel):
    display_name: str
    provider_id: str
    model_id: str
    provider_family: str | None = None
    order_index: int = Field(default=0, ge=0)
    context_view_id: str = "default"
    tool_policy_id: str = "none"
    generation_config: GenerationConfig = Field(default_factory=GenerationConfig)
    independence_mode: str = "ordinary"
    visibility_policy: str = "default"


class SeatRecord(SeatCreate):
    seat_id: str
    schema_version: int = 1


class RequestedCapabilities(StrictModel):
    required: set[str] = Field(default_factory=set)
    optional: set[str] = Field(default_factory=set)


class DispatchRequest(StrictModel):
    thread_id: str
    turn_parent: str | None = None
    prompt: str = Field(min_length=1)
    seat_ids: list[str] = Field(min_length=1)
    requested_capabilities: RequestedCapabilities = Field(default_factory=RequestedCapabilities)


class DispatchAccepted(StrictModel):
    dispatch_id: str
    run_ids: list[str]


class RunEvent(StrictModel):
    run_id: str
    sequence: int = Field(ge=1)
    event_type: str
    created_at: datetime
    data: dict[str, Any] = Field(default_factory=dict)


class RunReceipt(StrictModel):
    schema_version: int = 1
    run_id: str
    thread_id: str
    turn_parent: str | None
    seat_id: str
    provider_id: str
    model_id: str
    provider_family: str | None
    request_digest: str
    context_view_digest: str
    evidence_root_digest: str
    tool_policy_digest: str
    started_at: datetime
    first_token_at: datetime | None
    completed_at: datetime | None
    terminal_state: TerminalState
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost: float | None = None
    provider_request_id: str | None = None
    output_digest: str | None = None
    failure_class: FailureClass | None = None
    retry_of_run_id: str | None = None


class ThreadCreate(StrictModel):
    title: str | None = None


class ThreadRecord(StrictModel):
    thread_id: str
    title: str | None = None
    created_at: datetime
    run_count: int = 0
    last_run_at: datetime | None = None
    schema_version: int = 1

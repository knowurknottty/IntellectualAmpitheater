export type CapabilityState = "supported" | "unsupported" | "provider_default" | "unknown";

export type ProviderCapabilities = Record<string, CapabilityState>;

export type GenerationConfig = {
  temperature?: number | null;
  top_p?: number | null;
  seed?: number | null;
  max_output_tokens?: number | null;
  reasoning_control?: string | null;
};

export type SeatRecord = {
  seat_id: string;
  display_name: string;
  provider_id: string;
  model_id: string;
  provider_family?: string | null;
  order_index: number;
  context_view_id: string;
  tool_policy_id: string;
  generation_config: GenerationConfig;
  independence_mode: string;
  visibility_policy: string;
  schema_version: number;
};

export type ProviderSummary = {
  provider_id: string;
  display_name: string;
  adapter: string;
  base_url: string;
  provider_family?: string | null;
  max_concurrent_requests: number;
  capabilities: ProviderCapabilities;
  metadata: Record<string, unknown>;
};

export type DispatchRequest = {
  thread_id: string;
  turn_parent?: string | null;
  prompt: string;
  seat_ids: string[];
  requested_capabilities?: { required?: string[]; optional?: string[] };
};

export type DispatchAccepted = { dispatch_id: string; run_ids: string[] };

export type RunEvent = {
  run_id: string;
  sequence: number;
  event_type: string;
  created_at: string;
  data: Record<string, unknown>;
};

export type TerminalState = "completed" | "failed" | "cancelled_by_user" | "stream_interrupted" | "indeterminate";

export type RunReceipt = {
  schema_version: number;
  run_id: string;
  thread_id: string;
  turn_parent?: string | null;
  seat_id: string;
  provider_id: string;
  model_id: string;
  provider_family?: string | null;
  request_digest: string;
  context_view_digest: string;
  evidence_root_digest: string;
  tool_policy_digest: string;
  started_at: string;
  first_token_at?: string | null;
  completed_at?: string | null;
  terminal_state: TerminalState;
  input_tokens?: number | null;
  output_tokens?: number | null;
  estimated_cost?: number | null;
  provider_request_id?: string | null;
  output_digest?: string | null;
  failure_class?: string | null;
  retry_of_run_id?: string | null;
};

export type CancellationAcknowledgement = { run_id: string; cancel_requested: boolean };

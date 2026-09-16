import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(cleanup);

import type { ProviderSummary, RunReceipt } from "../src/api/types";
import { Composer } from "../src/components/Composer";
import { Inspector } from "../src/components/Inspector";
import { SeatGrid, type SeatView } from "../src/components/SeatGrid";

const seat = (id: string, name: string, overrides: Partial<SeatView> = {}): SeatView => ({
  seatId: id,
  displayName: name,
  providerId: "local-llama",
  providerLabel: "Local llama.cpp",
  modelLabel: `model-${id}`,
  status: "idle",
  ...overrides,
});

const provider = (overrides: Partial<ProviderSummary> = {}): ProviderSummary => ({
  provider_id: "local-llama",
  display_name: "Local llama.cpp",
  adapter: "openai_compat",
  base_url: "http://127.0.0.1:8080/v1",
  provider_family: "local",
  max_concurrent_requests: 1,
  capabilities: { streaming: "supported", temperature: "supported", web_search: "unsupported" },
  metadata: {},
  ...overrides,
});

describe("Composer", () => {
  it("dispatches to the explicitly selected seat without requiring a cloud provider", () => {
    const onDispatch = vi.fn();
    render(<Composer seats={[seat("a", "Alpha"), seat("b", "Beta")]} providers={[provider()]} onDispatch={onDispatch} onCancel={vi.fn()} />);
    fireEvent.click(screen.getByRole("checkbox", { name: "Beta" }));
    fireEvent.change(screen.getByLabelText("Prompt"), { target: { value: "Compare this." } });
    expect(screen.queryByText(/cloud provider required/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onDispatch).toHaveBeenCalledWith({
      prompt: "Compare this.",
      seatIds: ["a"],
      requestedCapabilities: { required: [], optional: [] },
    });
  });

  it("requires acknowledgement for optional capability loss", () => {
    render(<Composer seats={[seat("a", "Alpha")]} providers={[provider()]} optionalCapabilities={["web_search"]} onDispatch={vi.fn()} onCancel={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Prompt"), { target: { value: "Search if possible." } });
    expect(screen.getByText(/web_search.*unsupported/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    fireEvent.click(screen.getByRole("checkbox", { name: /acknowledge capability loss/i }));
    expect(screen.getByRole("button", { name: "Send" })).toBeEnabled();
  });

  it("blocks dispatch for a required unsupported capability", () => {
    render(<Composer seats={[seat("a", "Alpha")]} providers={[provider()]} requiredCapabilities={["web_search"]} onDispatch={vi.fn()} onCancel={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Prompt"), { target: { value: "Must search." } });
    expect(screen.getByText(/dispatch blocked/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("exposes stop at full action prominence while runs are active", () => {
    const onCancel = vi.fn();
    render(<Composer seats={[seat("a", "Alpha", { status: "running", runId: "run-a" })]} providers={[provider()]} onDispatch={vi.fn()} onCancel={onCancel} />);
    const stop = screen.getByRole("button", { name: "Stop active runs" });
    expect(stop).toHaveClass("composer-action", "composer-action--stop");
    fireEvent.click(stop);
    expect(onCancel).toHaveBeenCalledWith("run-a");
  });
});

describe("seat output and receipts", () => {
  it("preserves a successful sibling when another seat fails", () => {
    render(<SeatGrid seats={[
      seat("good", "Good", { status: "completed", text: "Useful answer" }),
      seat("bad", "Bad", { status: "failed", failureClass: "provider_timeout", text: "Partial" }),
    ]} />);
    expect(within(screen.getByRole("article", { name: /Good/i })).getByText("Useful answer")).toBeInTheDocument();
    const failed = screen.getByRole("article", { name: /Bad/i });
    expect(within(failed).getByText(/provider_timeout/)).toBeInTheDocument();
    expect(within(failed).getByText("Partial")).toBeInTheDocument();
  });

  it("shows receipt facts only when a real receipt exists", () => {
    const receipt: RunReceipt = {
      schema_version: 1, run_id: "run-a", thread_id: "thread-a", seat_id: "a",
      provider_id: "local-llama", model_id: "model-a", provider_family: "local",
      request_digest: "sha256:req", context_view_digest: "sha256:ctx", evidence_root_digest: "sha256:evidence",
      tool_policy_digest: "sha256:tools", started_at: "2026-09-16T00:00:00Z", first_token_at: "2026-09-16T00:00:01Z",
      completed_at: "2026-09-16T00:00:02Z", terminal_state: "completed", input_tokens: 10, output_tokens: 4,
      estimated_cost: null, provider_request_id: null, output_digest: "sha256:out", failure_class: null, retry_of_run_id: null,
    };
    const { rerender } = render(<Inspector seat={seat("a", "Alpha")} />);
    expect(screen.queryByText("sha256:req")).not.toBeInTheDocument();
    rerender(<Inspector seat={seat("a", "Alpha", { status: "completed", receipt })} />);
    expect(screen.getByText("sha256:req")).toBeInTheDocument();
    expect(screen.getByText("sha256:out")).toBeInTheDocument();
    expect(screen.getByText("10 input / 4 output")).toBeInTheDocument();
  });
});

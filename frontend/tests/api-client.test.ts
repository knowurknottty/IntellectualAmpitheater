import { describe, expect, it } from "vitest";

import { IntelAmpClient } from "../src/api/client";
import type { RunEvent } from "../src/api/types";
import { RunStore } from "../src/state/runStore";

function streamResponse(chunks: string[]): Response {
  const encoder = new TextEncoder();
  return new Response(
    new ReadableStream<Uint8Array>({
      start(controller) {
        for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
        controller.close();
      },
    }),
    { status: 200, headers: { "content-type": "text/event-stream" } },
  );
}

function event(runId: string, sequence: number, eventType: string, data: Record<string, unknown> = {}): RunEvent {
  return {
    run_id: runId,
    sequence,
    event_type: eventType,
    created_at: "2026-09-16T00:00:00Z",
    data,
  };
}

describe("IntelAmpClient SSE", () => {
  it("parses frames across byte boundaries", async () => {
    const fetchImpl: typeof fetch = async () => streamResponse([
      'id: 4\nevent: chunk\ndata: {"run_id":"run-1","sequence":4,"event_type":"chunk","created_at":"2026-09-16T00:00:00Z","data":{"text":"hel"}}\n',
      '\nid: 5\nevent: chunk\ndata: {"run_id":"run-1","sequence":5,"event_type":"chunk","created_at":"2026-09-16T00:00:01Z","data":{"text":"lo"}}\n\n',
    ]);
    const client = new IntelAmpClient({ baseUrl: "http://gateway.test", fetchImpl });
    const received: RunEvent[] = [];

    await client.subscribeRunEvents("run-1", {
      onEvent: (item) => { received.push(item); },
    });

    expect(received.map((item) => item.sequence)).toEqual([4, 5]);
    expect(received.map((item) => item.data.text)).toEqual(["hel", "lo"]);
  });

  it("propagates Last-Event-ID when resuming a run", async () => {
    let observedInit: RequestInit | undefined;
    const fetchImpl: typeof fetch = async (_input, init) => {
      observedInit = init;
      return streamResponse([]);
    };
    const client = new IntelAmpClient({ baseUrl: "http://gateway.test", fetchImpl });

    await client.subscribeRunEvents("run-9", {
      lastEventId: 17,
      onEvent: () => undefined,
    });

    expect(new Headers(observedInit?.headers).get("Last-Event-ID")).toBe("17");
  });
});

describe("IntelAmpClient typed actions", () => {
  it("returns typed cancellation acknowledgement", async () => {
    let observedInput: RequestInfo | URL | undefined;
    let observedInit: RequestInit | undefined;
    const fetchImpl: typeof fetch = async (input, init) => {
      observedInput = input;
      observedInit = init;
      return new Response(
        JSON.stringify({ run_id: "run-1", cancel_requested: true }),
        { status: 202, headers: { "content-type": "application/json" } },
      );
    };
    const client = new IntelAmpClient({ baseUrl: "http://gateway.test", fetchImpl });

    const result = await client.cancelRun("run-1");

    expect(result).toEqual({ run_id: "run-1", cancel_requested: true });
    expect(observedInput).toBe("http://gateway.test/api/runs/run-1/cancel");
    expect(observedInit?.method).toBe("POST");
  });
});

describe("RunStore partitioning", () => {
  it("replaces only the addressed run and preserves sibling object identity", () => {
    const store = new RunStore();
    store.applyEvent(event("run-a", 1, "queued"));
    store.applyEvent(event("run-b", 1, "queued"));
    const beforeA = store.getRun("run-a");
    const beforeB = store.getRun("run-b");

    store.applyEvent(event("run-a", 2, "chunk", { text: "hello" }));

    expect(store.getRun("run-a")).not.toBe(beforeA);
    expect(store.getRun("run-a")?.text).toBe("hello");
    expect(store.getRun("run-b")).toBe(beforeB);
  });

  it("records terminal state without mutating a sibling", () => {
    const store = new RunStore();
    store.applyEvent(event("run-a", 1, "running"));
    store.applyEvent(event("run-b", 1, "running"));
    const sibling = store.getRun("run-b");

    store.applyEvent(event("run-a", 2, "terminal", {
      terminal_state: "failed",
      failure_class: "provider_timeout",
    }));

    expect(store.getRun("run-a")?.terminalState).toBe("failed");
    expect(store.getRun("run-a")?.failureClass).toBe("provider_timeout");
    expect(store.getRun("run-b")).toBe(sibling);
  });
});

import type { RunEvent, TerminalState } from "../api/types";

export type RunPhase = "unknown" | "queued" | "running" | "terminal";

export type RunState = {
  runId: string;
  lastSequence: number;
  phase: RunPhase;
  text: string;
  terminalState?: TerminalState;
  failureClass?: string | null;
  usage?: Record<string, unknown>;
};

type Listener = () => void;

export class RunStore {
  private snapshot: ReadonlyMap<string, RunState> = new Map();
  private readonly listeners = new Set<Listener>();

  getSnapshot = (): ReadonlyMap<string, RunState> => this.snapshot;

  getRun(runId: string): RunState | undefined {
    return this.snapshot.get(runId);
  }

  subscribe = (listener: Listener): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  applyEvent(event: RunEvent): void {
    const current = this.snapshot.get(event.run_id) ?? {
      runId: event.run_id,
      lastSequence: 0,
      phase: "unknown" as const,
      text: "",
    };
    if (event.sequence <= current.lastSequence) return;

    let next: RunState = { ...current, lastSequence: event.sequence };
    if (event.event_type === "queued") next = { ...next, phase: "queued" };
    if (event.event_type === "running") next = { ...next, phase: "running" };
    if (event.event_type === "chunk" && typeof event.data.text === "string") {
      next = { ...next, text: current.text + event.data.text };
    }
    if (event.event_type === "usage") next = { ...next, usage: { ...event.data } };
    if (event.event_type === "terminal") {
      next = {
        ...next,
        phase: "terminal",
        terminalState: event.data.terminal_state as TerminalState,
        failureClass: typeof event.data.failure_class === "string" ? event.data.failure_class : null,
      };
    }

    const updated = new Map(this.snapshot);
    updated.set(event.run_id, next);
    this.snapshot = updated;
    for (const listener of this.listeners) listener();
  }
}

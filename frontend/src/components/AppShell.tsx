import { useEffect, useMemo, useRef, useState } from "react";
import { IntelAmpClient } from "../api/client";
import type { ProviderSummary, RunEvent, SeatRecord, ThreadRecord } from "../api/types";
import { Composer } from "./Composer";
import { Inspector } from "./Inspector";
import { SeatGrid, type SeatStatus, type SeatView } from "./SeatGrid";

type DispatchIntent = { prompt: string; seatIds: string[]; requestedCapabilities: { required: string[]; optional: string[] } };
type AppShellProps = {
  seats?: SeatView[];
  providers?: ProviderSummary[];
  client?: IntelAmpClient;
  onDispatch?: (intent: DispatchIntent) => void | Promise<void>;
  onCancel?: (runId: string) => void | Promise<void>;
};

function focusRegion(id: string) { document.getElementById(id)?.focus(); }
function statusFromEvent(event: RunEvent): SeatStatus | undefined {
  if (event.event_type === "queued") return "queued";
  if (event.event_type === "running") return "running";
  if (event.event_type !== "terminal") return undefined;
  const terminal = event.data.terminal_state;
  if (terminal === "completed" || terminal === "cancelled_by_user" || terminal === "stream_interrupted" || terminal === "indeterminate") return terminal;
  return "failed";
}
function toSeatView(seat: SeatRecord, providers: ProviderSummary[]): SeatView {
  const provider = providers.find((candidate) => candidate.provider_id === seat.provider_id);
  return { seatId: seat.seat_id, displayName: seat.display_name, providerId: seat.provider_id, providerLabel: provider?.display_name ?? seat.provider_id, modelLabel: seat.model_id, status: "idle" };
}

export function AppShell({ seats: controlledSeats, providers: controlledProviders, client, onDispatch, onCancel }: AppShellProps) {
  const gateway = useMemo(() => client ?? new IntelAmpClient(), [client]);
  const [liveSeats, setLiveSeats] = useState<SeatView[]>(controlledSeats ?? []);
  const [liveProviders, setLiveProviders] = useState<ProviderSummary[]>(controlledProviders ?? []);
  const [focusedSeatId, setFocusedSeatId] = useState((controlledSeats ?? [])[0]?.seatId ?? "");
  const [gatewayError, setGatewayError] = useState<string | null>(null);
  const [threads, setThreads] = useState<ThreadRecord[]>([]);
  const [activeThreadId, setActiveThreadId] = useState("");
  const runToSeat = useRef(new Map<string, string>());

  useEffect(() => { if (controlledSeats) setLiveSeats(controlledSeats); }, [controlledSeats]);
  useEffect(() => { if (controlledProviders) setLiveProviders(controlledProviders); }, [controlledProviders]);
  useEffect(() => {
    if (controlledSeats || controlledProviders) return;
    let active = true;
    void Promise.all([gateway.listProviders(), gateway.listSeats(), gateway.listThreads()]).then(([providers, seats, threadList]) => {
      if (!active) return;
      setLiveProviders(providers); setLiveSeats(seats.map((seat) => toSeatView(seat, providers))); setFocusedSeatId((current) => current || seats[0]?.seat_id || "");
      setThreads(threadList); setActiveThreadId((current) => current || threadList[0]?.thread_id || "");
    }).catch((error: unknown) => { if (active) setGatewayError(error instanceof Error ? error.message : "Gateway unavailable"); });
    return () => { active = false; };
  }, [controlledProviders, controlledSeats, gateway]);

  useEffect(() => {
    if (!liveSeats.some((seat) => seat.seatId === focusedSeatId)) setFocusedSeatId(liveSeats[0]?.seatId ?? "");
  }, [focusedSeatId, liveSeats]);

  const applyEvent = (runId: string, event: RunEvent) => {
    const seatId = runToSeat.current.get(runId); if (!seatId) return;
    setLiveSeats((current) => current.map((seat) => {
      if (seat.seatId !== seatId) return seat;
      const status = statusFromEvent(event) ?? seat.status;
      const text = event.event_type === "chunk" && typeof event.data.text === "string" ? (seat.text ?? "") + event.data.text : seat.text;
      const failureClass = event.event_type === "terminal" && typeof event.data.failure_class === "string" ? event.data.failure_class : seat.failureClass;
      return { ...seat, status, text, failureClass };
    }));
  };

  const adoptThread = (created: ThreadRecord) => {
    setActiveThreadId(created.thread_id);
    setThreads((current) => [created, ...current.filter((thread) => thread.thread_id !== created.thread_id)]);
  };

  const newThread = async () => {
    try { adoptThread(await gateway.createThread()); }
    catch (error: unknown) { setGatewayError(error instanceof Error ? error.message : "Thread creation failed"); }
  };

  const dispatch = async (intent: DispatchIntent) => {
    if (onDispatch) return await onDispatch(intent);
    setGatewayError(null);
    let threadId = activeThreadId;
    if (!threadId) {
      const created = await gateway.createThread();
      threadId = created.thread_id;
      adoptThread(created);
    }
    const accepted = await gateway.dispatch({ thread_id: threadId, prompt: intent.prompt, seat_ids: intent.seatIds, requested_capabilities: intent.requestedCapabilities });
    intent.seatIds.forEach((seatId, index) => { const runId = accepted.run_ids[index]; if (runId) runToSeat.current.set(runId, seatId); });
    setLiveSeats((current) => current.map((seat) => intent.seatIds.includes(seat.seatId) ? { ...seat, status: "queued", runId: accepted.run_ids[intent.seatIds.indexOf(seat.seatId)], text: "", failureClass: null, receipt: undefined } : seat));
    void gateway.listThreads().then((fresh) => setThreads(fresh)).catch(() => undefined);
    accepted.run_ids.forEach((runId) => {
      void gateway.subscribeRunEvents(runId, { onEvent: (event) => applyEvent(runId, event) }).then(async () => {
        const receipt = await gateway.getReceipt(runId); const seatId = runToSeat.current.get(runId);
        if (seatId) setLiveSeats((current) => current.map((seat) => seat.seatId === seatId ? { ...seat, receipt } : seat));
      }).catch((error: unknown) => setGatewayError(error instanceof Error ? error.message : "Run stream failed"));
    });
  };
  const cancel = async (runId: string) => { if (onCancel) return await onCancel(runId); await gateway.cancelRun(runId); };

  const focusedSeat = liveSeats.find((seat) => seat.seatId === focusedSeatId) ?? liveSeats[0];
  const activeCount = liveSeats.filter((seat) => seat.status === "queued" || seat.status === "running").length;
  return <div className="intelamp-shell">
    <nav className="workspace-nav" aria-label="Workspace navigation"><div className="brand-mark" aria-label="IntelAMP">IA</div><button type="button" onClick={() => focusRegion("seat-workspace")}>Threads</button><button type="button" onClick={() => focusRegion("inspector")}>Providers</button><button type="button" onClick={() => focusRegion("composer")}>Compose</button></nav>
    <header className="run-status" aria-label="Run status"><div><span className="run-status__brand">INTELAMP</span><span className="run-status__divider" aria-hidden="true">/</span><span>{liveSeats.length} {liveSeats.length === 1 ? "seat" : "seats"}</span></div><strong>{activeCount > 0 ? `${activeCount} running` : "No active run"}</strong></header>
    <main id="seat-workspace" className="seat-workspace" aria-label="Seat workspace" tabIndex={-1}>{gatewayError && <p className="gateway-error" role="alert">{gatewayError}</p>}<div className="thread-control"><label><span>Thread</span><select aria-label="Thread" value={activeThreadId} onChange={(event) => setActiveThreadId(event.target.value)}>{threads.map((thread) => <option value={thread.thread_id} key={thread.thread_id}>{thread.title ?? thread.thread_id}</option>)}</select></label><button type="button" onClick={() => void newThread()}>New thread</button></div>{liveSeats.length > 0 && <label className="focused-seat-control"><span>Focused seat</span><select aria-label="Focused seat" value={focusedSeat?.seatId ?? ""} onChange={(event) => setFocusedSeatId(event.target.value)}>{liveSeats.map((seat) => <option value={seat.seatId} key={seat.seatId}>{seat.displayName}</option>)}</select></label>}<SeatGrid seats={liveSeats} focusedSeatId={focusedSeat?.seatId} /></main>
    <div id="composer" tabIndex={-1}><Composer seats={liveSeats} providers={liveProviders} onDispatch={dispatch} onCancel={cancel} /></div>
    <div id="inspector" tabIndex={-1}><Inspector seat={focusedSeat} /></div>
  </div>;
}

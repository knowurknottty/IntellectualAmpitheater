import { useEffect, useMemo, useState } from "react";
import type { ProviderSummary } from "../api/types";
import type { SeatView } from "./SeatGrid";
import { ProviderWarnings } from "./ProviderWarnings";

type DispatchIntent = { prompt: string; seatIds: string[]; requestedCapabilities: { required: string[]; optional: string[] } };
type ComposerProps = {
  seats: SeatView[];
  providers: ProviderSummary[];
  requiredCapabilities?: string[];
  optionalCapabilities?: string[];
  onDispatch: (intent: DispatchIntent) => void | Promise<void>;
  onCancel: (runId: string) => void | Promise<void>;
};

function issueText(seat: SeatView, capability: string, state: string): string {
  return `${seat.displayName}: ${capability} is ${state}`;
}

export function Composer({ seats, providers, requiredCapabilities = [], optionalCapabilities = [], onDispatch, onCancel }: ComposerProps) {
  const [prompt, setPrompt] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>(() => seats.map((seat) => seat.seatId));
  const [acknowledged, setAcknowledged] = useState(false);

  useEffect(() => {
    setSelectedIds((current) => {
      const valid = current.filter((id) => seats.some((seat) => seat.seatId === id));
      return valid.length > 0 ? valid : seats.map((seat) => seat.seatId);
    });
  }, [seats]);

  const selectedSeats = seats.filter((seat) => selectedIds.includes(seat.seatId));
  const issues = useMemo(() => {
    const hard: string[] = [];
    const warnings: string[] = [];
    for (const seat of selectedSeats) {
      const definition = providers.find((candidate) => candidate.provider_id === seat.providerId);
      if (!definition) {
        hard.push(`${seat.displayName}: provider is unavailable`);
        continue;
      }
      for (const capability of requiredCapabilities) {
        const state = definition.capabilities[capability] ?? "unknown";
        if (state !== "supported") hard.push(issueText(seat, capability, state));
      }
      for (const capability of optionalCapabilities) {
        const state = definition.capabilities[capability] ?? "unknown";
        if (state !== "supported") warnings.push(issueText(seat, capability, state));
      }
    }
    return { hard, warnings };
  }, [optionalCapabilities, providers, requiredCapabilities, selectedSeats]);

  const issueSignature = [...issues.hard, ...issues.warnings].join("\u0000");
  useEffect(() => { setAcknowledged(false); }, [issueSignature]);

  const activeRunIds = Array.from(new Set(seats
    .filter((seat) => (seat.status === "queued" || seat.status === "running") && seat.runId)
    .map((seat) => seat.runId as string)));
  const allSelected = seats.length > 0 && selectedIds.length === seats.length;
  const canDispatch = prompt.trim().length > 0 && selectedIds.length > 0 && issues.hard.length === 0 && (issues.warnings.length === 0 || acknowledged);

  return (
    <form className="composer" aria-label="Prompt composer" onSubmit={(event) => {
      event.preventDefault();
      if (!canDispatch) return;
      void onDispatch({ prompt: prompt.trim(), seatIds: selectedIds, requestedCapabilities: { required: requiredCapabilities, optional: optionalCapabilities } });
    }}>
      <fieldset className="composer-targets">
        <legend>Targets</legend>
        <label><input type="checkbox" checked={allSelected} onChange={(event) => setSelectedIds(event.target.checked ? seats.map((seat) => seat.seatId) : [])} />All seats</label>
        {seats.map((seat) => (
          <label key={seat.seatId}><input type="checkbox" checked={selectedIds.includes(seat.seatId)} onChange={(event) => setSelectedIds((current) => event.target.checked ? [...current, seat.seatId] : current.filter((id) => id !== seat.seatId))} />{seat.displayName}</label>
        ))}
      </fieldset>
      <label className="composer-prompt" htmlFor="prompt">Prompt</label>
      <textarea id="prompt" name="prompt" rows={2} value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Ask the selected seats" />
      <ProviderWarnings warnings={issues.warnings} hardIncompatibilities={issues.hard} acknowledged={acknowledged} onAcknowledgedChange={setAcknowledged} />
      <div className="composer-actions">
        <button className="composer-action composer-action--send" type="submit" disabled={!canDispatch}>Send</button>
        {activeRunIds.length > 0 && <button className="composer-action composer-action--stop" type="button" onClick={() => activeRunIds.forEach((runId) => void onCancel(runId))}>Stop active runs</button>}
      </div>
    </form>
  );
}

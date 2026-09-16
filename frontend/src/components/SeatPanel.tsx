import { memo } from "react";
import type { SeatView } from "./SeatGrid";

type SeatPanelProps = { seat: SeatView; focused: boolean };

function statusCopy(seat: SeatView): string {
  if (seat.text) return seat.text;
  if (seat.status === "queued") return "Queued for provider capacity.";
  if (seat.status === "running") return "Waiting for provider output.";
  if (seat.status === "completed") return "Run completed without answer text.";
  if (seat.status === "cancelled_by_user") return "Cancelled by user.";
  if (seat.status === "stream_interrupted") return "Stream interrupted. Partial output is preserved.";
  if (seat.status === "indeterminate") return "Run terminal state is indeterminate.";
  if (seat.status === "failed") return "Run failed.";
  return "No run is active in this seat.";
}

export const SeatPanel = memo(function SeatPanel({ seat, focused }: SeatPanelProps) {
  return (
    <article className="seat-panel" data-focused={focused ? "true" : "false"} data-status={seat.status} aria-label={`${seat.displayName} seat`}>
      <header className="seat-panel__header">
        <div><p className="eyebrow">{seat.providerLabel}</p><h2>{seat.displayName}</h2></div>
        <span className="seat-status">{seat.status.replaceAll("_", " ")}</span>
      </header>
      <div className="seat-panel__body">
        <p className="model-label">{seat.modelLabel}</p>
        {seat.failureClass && <p className="seat-failure">{seat.failureClass}</p>}
        <p className="seat-copy">{statusCopy(seat)}</p>
      </div>
    </article>
  );
});

import type { RunReceipt } from "../api/types";
import { SeatPanel } from "./SeatPanel";

export type SeatStatus = "idle" | "queued" | "running" | "completed" | "failed" | "cancelled_by_user" | "stream_interrupted" | "indeterminate";
export type SeatView = {
  seatId: string;
  displayName: string;
  providerId?: string;
  providerLabel: string;
  modelLabel: string;
  status: SeatStatus;
  runId?: string;
  text?: string;
  failureClass?: string | null;
  receipt?: RunReceipt;
};
type SeatGridProps = { seats: SeatView[]; focusedSeatId?: string };

function layoutFor(count: number): string {
  if (count === 0) return "empty";
  if (count === 1) return "single";
  if (count === 6) return "six";
  return "adaptive";
}

export function SeatGrid({ seats, focusedSeatId }: SeatGridProps) {
  const layout = layoutFor(seats.length);
  return (
    <section className="seat-grid" data-layout={layout} data-seat-count={seats.length} data-testid="seat-grid" aria-label="Model seats">
      {seats.length === 0 ? <div className="empty-state"><p className="eyebrow">NO SEATS CONFIGURED</p><h2>Start with one model. Add contrast only when it earns its space.</h2><p>Provider configuration is local to this installation.</p></div>
        : seats.map((seat) => <SeatPanel key={seat.seatId} seat={seat} focused={focusedSeatId ? seat.seatId === focusedSeatId : true} />)}
    </section>
  );
}

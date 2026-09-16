export type SeatStatus = "idle" | "queued" | "running" | "completed" | "failed" | "cancelled";

export type SeatView = {
  seatId: string;
  displayName: string;
  providerLabel: string;
  modelLabel: string;
  status: SeatStatus;
};

type SeatGridProps = {
  seats: SeatView[];
  focusedSeatId?: string;
};

function layoutFor(count: number): string {
  if (count === 0) return "empty";
  if (count === 1) return "single";
  if (count === 6) return "six";
  return "adaptive";
}

export function SeatGrid({ seats, focusedSeatId }: SeatGridProps) {
  const layout = layoutFor(seats.length);

  return (
    <section
      className="seat-grid"
      data-layout={layout}
      data-seat-count={seats.length}
      data-testid="seat-grid"
      aria-label="Model seats"
    >
      {seats.length === 0 ? (
        <div className="empty-state">
          <p className="eyebrow">NO SEATS CONFIGURED</p>
          <h2>Start with one model. Add contrast only when it earns its space.</h2>
          <p>Provider configuration is local to this installation.</p>
        </div>
      ) : (
        seats.map((seat) => {
          const focused = focusedSeatId ? seat.seatId === focusedSeatId : true;
          return (
            <article
              className="seat-panel"
              data-focused={focused ? "true" : "false"}
              data-status={seat.status}
              key={seat.seatId}
              aria-labelledby={`${seat.seatId}-title`}
            >
              <header className="seat-panel__header">
                <div>
                  <p className="eyebrow">{seat.providerLabel}</p>
                  <h2 id={`${seat.seatId}-title`}>{seat.displayName}</h2>
                </div>
                <span className="seat-status">{seat.status.replace("_", " ")}</span>
              </header>
              <div className="seat-panel__body">
                <p className="model-label">{seat.modelLabel}</p>
                <p className="seat-copy">No run is active in this seat.</p>
              </div>
            </article>
          );
        })
      )}
    </section>
  );
}

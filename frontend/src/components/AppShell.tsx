import { useEffect, useState } from "react";

import { SeatGrid, type SeatView } from "./SeatGrid";

type AppShellProps = {
  seats: SeatView[];
};

function focusRegion(id: string) {
  document.getElementById(id)?.focus();
}

export function AppShell({ seats }: AppShellProps) {
  const [focusedSeatId, setFocusedSeatId] = useState(seats[0]?.seatId ?? "");

  useEffect(() => {
    if (!seats.some((seat) => seat.seatId === focusedSeatId)) {
      setFocusedSeatId(seats[0]?.seatId ?? "");
    }
  }, [focusedSeatId, seats]);

  const focusedSeat = seats.find((seat) => seat.seatId === focusedSeatId) ?? seats[0];

  return (
    <div className="intelamp-shell">
      <nav className="workspace-nav" aria-label="Workspace navigation">
        <div className="brand-mark" aria-label="IntelAMP">IA</div>
        <button type="button" onClick={() => focusRegion("seat-workspace")}>Threads</button>
        <button type="button" onClick={() => focusRegion("inspector")}>Providers</button>
        <button type="button" onClick={() => focusRegion("composer")}>Compose</button>
      </nav>

      <header className="run-status" aria-label="Run status">
        <div>
          <span className="run-status__brand">INTELAMP</span>
          <span className="run-status__divider" aria-hidden="true">/</span>
          <span>{seats.length} {seats.length === 1 ? "seat" : "seats"}</span>
        </div>
        <strong>No active run</strong>
      </header>

      <main id="seat-workspace" className="seat-workspace" aria-label="Seat workspace" tabIndex={-1}>
        {seats.length > 0 && (
          <label className="focused-seat-control">
            <span>Focused seat</span>
            <select
              aria-label="Focused seat"
              value={focusedSeat?.seatId ?? ""}
              onChange={(event) => setFocusedSeatId(event.target.value)}
            >
              {seats.map((seat) => (
                <option value={seat.seatId} key={seat.seatId}>{seat.displayName}</option>
              ))}
            </select>
          </label>
        )}
        <SeatGrid seats={seats} focusedSeatId={focusedSeat?.seatId} />
      </main>

      <form id="composer" className="composer" aria-label="Prompt composer" tabIndex={-1} onSubmit={(event) => event.preventDefault()}>
        <label htmlFor="prompt">Prompt</label>
        <textarea
          id="prompt"
          name="prompt"
          rows={2}
          disabled
          placeholder="Gateway client not connected in this shell build"
        />
        <span className="composer__state">Dispatch is unavailable until the typed gateway client is attached.</span>
      </form>

      <aside id="inspector" className="inspector" aria-label="Inspector" tabIndex={-1}>
        <p className="eyebrow">INSPECTOR</p>
        <h2>{focusedSeat?.displayName ?? "No seat selected"}</h2>
        {focusedSeat ? (
          <dl>
            <div><dt>Provider</dt><dd>{focusedSeat.providerLabel}</dd></div>
            <div><dt>Model</dt><dd>{focusedSeat.modelLabel}</dd></div>
            <div><dt>State</dt><dd>{focusedSeat.status}</dd></div>
          </dl>
        ) : (
          <p>Configure a seat to inspect provider and model identity.</p>
        )}
      </aside>
    </div>
  );
}

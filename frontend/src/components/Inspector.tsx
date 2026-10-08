import { useState } from "react";
import type { IntelAmpClient } from "../api/client";
import type { RunContext } from "../api/types";
import type { SeatView } from "./SeatGrid";

type InspectorProps = { seat?: SeatView; client?: IntelAmpClient };

export function Inspector({ seat, client }: InspectorProps) {
  const [context, setContext] = useState<RunContext | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  if (!seat) return <aside className="inspector" aria-label="Inspector"><p className="eyebrow">INSPECTOR</p><h2>No seat selected</h2><p>Configure a seat to inspect provider and model identity.</p></aside>;
  const receipt = seat.receipt;

  async function showContext() {
    if (!client || !receipt) return;
    setContextError(null);
    try {
      setContext(await client.getRunContext(receipt.run_id));
    } catch (error: unknown) {
      setContextError(error instanceof Error ? error.message : "Context unavailable");
    }
  }
  return (
    <aside className="inspector" aria-label="Inspector">
      <p className="eyebrow">INSPECTOR</p><h2>{seat.displayName}</h2>
      <dl>
        <div><dt>Provider</dt><dd>{seat.providerLabel}</dd></div>
        <div><dt>Model</dt><dd>{seat.modelLabel}</dd></div>
        <div><dt>State</dt><dd>{seat.status.replaceAll("_", " ")}</dd></div>
        {seat.failureClass && <div><dt>Failure class</dt><dd>{seat.failureClass}</dd></div>}
      </dl>
      {receipt && <section className="receipt-facts" aria-label="Run receipt">
        <h3>Receipt</h3><dl>
          <div><dt>Run</dt><dd>{receipt.run_id}</dd></div>
          <div><dt>Request digest</dt><dd>{receipt.request_digest}</dd></div>
          <div><dt>Context digest</dt><dd>{receipt.context_view_digest}</dd></div>
          <div><dt>Output digest</dt><dd>{receipt.output_digest ?? "Not reported"}</dd></div>
          <div><dt>Tokens</dt><dd>{receipt.input_tokens ?? "unknown"} input / {receipt.output_tokens ?? "unknown"} output</dd></div>
          <div><dt>Started (gateway UTC)</dt><dd>{receipt.started_at}</dd></div>
          {receipt.first_token_at && <div><dt>First token (gateway UTC)</dt><dd>{receipt.first_token_at}</dd></div>}
          {receipt.completed_at && <div><dt>Completed (gateway UTC)</dt><dd>{receipt.completed_at}</dd></div>}
        </dl>
        {client && !context && <button type="button" onClick={() => void showContext()}>What it saw</button>}
        {contextError && <p role="alert">{contextError}</p>}
        {context && (context.messages
          ? <ol className="context-list" aria-label="Exact messages sent to the provider">
              {context.messages.map((message, index) => (
                <li key={index}><strong>{message.role}</strong><pre>{message.content}</pre></li>
              ))}
            </ol>
          : <p>Context was not recorded for this run.</p>)}
      </section>}
    </aside>
  );
}

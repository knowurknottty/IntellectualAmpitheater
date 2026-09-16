import type {
  CancellationAcknowledgement,
  DispatchAccepted,
  DispatchRequest,
  ProviderSummary,
  RunEvent,
  RunReceipt,
  SeatRecord,
} from "./types";

export class IntelAmpApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "IntelAmpApiError";
  }
}

type ClientOptions = {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
};

type SubscribeOptions = {
  lastEventId?: number;
  signal?: AbortSignal;
  onEvent: (event: RunEvent) => void | Promise<void>;
};

export class IntelAmpClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor({ baseUrl = "", fetchImpl = fetch }: ClientOptions = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.fetchImpl = fetchImpl;
  }

  private url(path: string): string {
    return `${this.baseUrl}${path}`;
  }

  private async checked(response: Response): Promise<Response> {
    if (response.ok) return response;
    let code = "http_error";
    let message = `IntelAMP gateway returned HTTP ${response.status}`;
    try {
      const body = await response.json() as { error?: { code?: string; message?: string } };
      code = body.error?.code ?? code;
      message = body.error?.message ?? message;
    } catch {
      // Preserve the transport-level fallback without inventing a structured error.
    }
    throw new IntelAmpApiError(response.status, code, message);
  }

  private async json<T>(path: string, init?: RequestInit): Promise<T> {
    const headers = new Headers(init?.headers);
    if (init?.body !== undefined && !headers.has("content-type")) headers.set("content-type", "application/json");
    const response = await this.fetchImpl(this.url(path), { ...init, headers });
    await this.checked(response);
    return await response.json() as T;
  }

  async listSeats(): Promise<SeatRecord[]> {
    return (await this.json<{ seats: SeatRecord[] }>("/api/seats")).seats;
  }

  async createSeat(seat: Omit<SeatRecord, "seat_id" | "schema_version">): Promise<SeatRecord> {
    return await this.json<SeatRecord>("/api/seats", { method: "POST", body: JSON.stringify(seat) });
  }

  async patchSeat(seatId: string, changes: Partial<Omit<SeatRecord, "seat_id" | "schema_version">>): Promise<SeatRecord> {
    return await this.json<SeatRecord>(`/api/seats/${encodeURIComponent(seatId)}`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    });
  }

  async deleteSeat(seatId: string): Promise<void> {
    const response = await this.fetchImpl(this.url(`/api/seats/${encodeURIComponent(seatId)}`), { method: "DELETE" });
    await this.checked(response);
  }

  async listProviders(): Promise<ProviderSummary[]> {
    return (await this.json<{ providers: ProviderSummary[] }>("/api/providers")).providers;
  }

  async dispatch(request: DispatchRequest): Promise<DispatchAccepted> {
    return await this.json<DispatchAccepted>("/api/dispatch", { method: "POST", body: JSON.stringify(request) });
  }

  async cancelRun(runId: string): Promise<CancellationAcknowledgement> {
    return await this.json<CancellationAcknowledgement>(`/api/runs/${encodeURIComponent(runId)}/cancel`, { method: "POST" });
  }

  async getReceipt(runId: string): Promise<RunReceipt> {
    return await this.json<RunReceipt>(`/api/runs/${encodeURIComponent(runId)}/receipt`);
  }

  async subscribeRunEvents(runId: string, options: SubscribeOptions): Promise<void> {
    const headers = new Headers({ accept: "text/event-stream" });
    if (options.lastEventId !== undefined) headers.set("Last-Event-ID", String(options.lastEventId));
    const response = await this.fetchImpl(this.url(`/api/runs/${encodeURIComponent(runId)}/events`), {
      method: "GET",
      headers,
      signal: options.signal,
    });
    await this.checked(response);
    if (!response.body) throw new IntelAmpApiError(502, "stream_missing", "Gateway returned an SSE response without a body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/\r\n/g, "\n");
        let boundary = buffer.indexOf("\n\n");
        while (boundary >= 0) {
          const frame = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          const event = parseFrame(frame);
          if (event) await options.onEvent(event);
          boundary = buffer.indexOf("\n\n");
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

function parseFrame(frame: string): RunEvent | null {
  let id: number | undefined;
  const data: string[] = [];
  for (const line of frame.split("\n")) {
    if (line.startsWith("id:")) id = Number(line.slice(3).trim());
    if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }
  if (data.length === 0) return null;
  const event = JSON.parse(data.join("\n")) as RunEvent;
  if (id !== undefined && id !== event.sequence) {
    throw new IntelAmpApiError(502, "sse_sequence_mismatch", `SSE id ${id} did not match event sequence ${event.sequence}`);
  }
  return event;
}

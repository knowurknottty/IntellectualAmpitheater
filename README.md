# IntellectualAmpitheater (IntelAMP)

IntelAMP is a local-first multi-model workbench from Inversion Labs. Tranche 0 is the contract-and-shell vertical slice: typed provider capabilities, durable local runs, real OpenAI-compatible streaming, isolated multi-seat dispatch, resumable SSE, receipts, and a responsive operating surface.

This repository does **not** claim the later Context Topology Matrix, Conversation Git, Replay Lab, Tool Shadow, ThreadCapsules, or False-Consensus Firewall are implemented. Those remain tracked as `unverified` in `PARITY_LEDGER.md` until their own evidence exists.

## What is verified in Tranche 0

- Python 3.12 FastAPI gateway with Pydantic contracts.
- SQLite/WAL persistence for seats, runs, ordered events, partial output, and terminal receipts.
- Four-state provider capability registry and pre-dispatch capability compilation.
- Real OpenAI-compatible SSE adapter.
- Real local llama.cpp acceptance on `127.0.0.1:8080` with no cloud credential.
- Provider concurrency limits, sibling failure isolation, cancellation, retry lineage, and no silent provider/model substitution.
- HTTP API with resumable per-run SSE using `Last-Event-ID`.
- React/TypeScript seat shell, targetable composer, capability-loss acknowledgement, Stop action, typed failure states, and receipt inspector.
- Mobile-focused seat behavior, `100dvh`, 44 px controls, 16 px mobile prompt input, visible focus, and reduced-motion CSS.

Evidence lives under `evidence/`. Unit fixtures are never treated as provider-integration evidence.

## Local quick start

Prerequisites: Python 3.12+, `uv`, Node 22+, npm, and a llama.cpp OpenAI-compatible server. The example provider expects `http://127.0.0.1:8080/v1` and does not require an API key.

```bash
uv sync --project backend
npm ci --prefix frontend
./scripts/dev.sh
```

Open `http://127.0.0.1:5173`. The dev server proxies `/api` to the loopback gateway on port `8787`.

The first run applies Alembic migrations to `./intelamp.sqlite3`. Provider definitions are loaded from `config/providers.example.toml`. Stored provider secrets are not returned to the browser and are not written into the conversation database.

## Verification

```bash
uv run --project backend pytest backend/tests -q
npm --prefix frontend test -- --run
npm --prefix frontend run typecheck
npm --prefix frontend run build
./scripts/provenance_guard.py backend/src frontend/src
```

The provenance guard is a narrow tripwire, not proof of legal cleanliness. See `THIRD_PARTY.md`.

## Architecture boundary

IntelAMP owns its shell, contracts, durable model, capability semantics, and run evidence. Open WebUI and ChatHub-family projects are references or future adapters/sidecars, not the application root. Ordinary IntelAMP seats are not represented as CAPT vessels unless CAPT itself establishes that governed identity.

## Failure semantics

Failures remain explicit. Partial output is preserved. Interrupted streams are not rewritten as completed. One failed seat does not erase successful sibling receipts. Unsupported required capabilities block dispatch; optional capability loss is surfaced rather than silently ignored.

## Project truth discipline

Claims in README and UI should be traceable to tests or evidence. If an integration was not actually run, it remains `UNVERIFIED`. Novelty of the planned False-Consensus Firewall remains a research question pending dedicated prior-art review.

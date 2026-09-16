# IntellectualAmpitheater Tranche 0 Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a locally hosted IntelAMP vertical slice with persistent seats, a typed provider registry and capability compiler, real OpenAI-compatible streaming against local llama.cpp, isolated multi-seat runs, durable receipts/events, cancellation, and an accessible responsive React shell.

**Architecture:** React/TypeScript/Vite is a thin operating surface over a Python 3.12+ FastAPI gateway. SQLite/WAL owns local durable metadata and stream events; provider secrets never enter the browser or conversation database. Ordinary multi-seat dispatch uses gateway scheduling with per-provider concurrency limits and is explicitly not represented as CAPT cohort/vessel execution.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, httpx, SQLite/WAL, pytest; React 19, TypeScript, Vite, Vitest, Testing Library, Tailwind CSS v4.

**Spec:** `docs/superpowers/specs/2026-09-15-intellectualampitheater-design.md`

## Global Constraints

- Architecture A remains frozen: Inversion-native shell plus clean adapters.
- `EXTRACTION: 0`; product surfaces are `OPERATE`, `CAPTURE: 2/10`; NIGHT TABLE is the starting palette.
- Browser never receives stored provider secrets and never becomes receipt authority.
- Local-only use must work with the llama.cpp OpenAI-compatible server and no cloud credentials.
- Unsupported provider controls are surfaced before dispatch; no silent degradation or model substitution.
- One seat failure cannot erase successful sibling output or receipts.
- Ordinary seats are never called CAPT vessels unless live CAPT authority establishes that identity.
- Every persisted record has a schema version; interrupted streams never become fabricated `completed` runs.
- Full-height mobile shell uses `100dvh`; controls are at least 44 px; inputs are at least 16 px on mobile; reduced motion is supported.
- GPL ChatHub source is reference-only for this core. Open WebUI remains a sidecar boundary. MIT ChatHub use must preserve notice if code is later imported.
- Tranche 0 does not claim the False-Consensus Firewall, Conversation Git, Replay, or CAPT tool execution are implemented; their contracts remain future tranches.

---

## File Structure

```text
backend/
  pyproject.toml
  alembic.ini
  migrations/env.py
  migrations/versions/0001_initial.py
  src/intelamp/
    app.py                 # FastAPI assembly/lifespan
    config.py              # non-secret provider/runtime config
    contracts.py           # Pydantic API/domain contracts
    database.py            # engine/session/WAL setup
    models.py              # SQLAlchemy durable models
    repositories.py        # seat/thread/run/event persistence
    capabilities.py        # capability compiler
    providers/base.py      # provider protocol and stream event types
    providers/openai_compat.py # real OpenAI-compatible adapter
    registry.py            # provider definitions/adapters + semaphores
    dispatch.py            # ordinary seat dispatch lifecycle
    routes.py              # HTTP/SSE API
  tests/
    test_contracts.py
    test_database.py
    test_capabilities.py
    test_registry.py
    test_openai_compat.py
    test_dispatch.py
    test_routes.py
frontend/
  package.json
  vite.config.ts
  tsconfig*.json
  src/
    main.tsx
    styles.css
    api/types.ts
    api/client.ts
    state/runStore.ts
    components/AppShell.tsx
    components/SeatGrid.tsx
    components/SeatPanel.tsx
    components/Composer.tsx
    components/ProviderWarnings.tsx
    components/Inspector.tsx
  tests/
    api-client.test.ts
    seat-grid.test.tsx
    composer.test.tsx
config/providers.example.toml
scripts/dev.sh
THIRD_PARTY.md
PARITY_LEDGER.md
README.md
```

## Task 1: Backend packaging and typed contracts

**Files:** Create `backend/pyproject.toml`, `backend/src/intelamp/__init__.py`, `backend/src/intelamp/contracts.py`, `backend/tests/test_contracts.py`.

**Interfaces:** Produces `CapabilityState`, `ProviderCapabilities`, `ProviderDefinition`, `SeatCreate`, `SeatRecord`, `DispatchRequest`, `DispatchAccepted`, `RunEvent`, `RunReceipt`, `FailureClass`, and `TerminalState`.

- [ ] **Step 1: Write the failing contract tests** asserting invalid capability states fail, optional usage fields remain `None`, failure/terminal enums reject unknown values, and a receipt round-trip preserves digests exactly.
- [ ] **Step 2: Run** `uv run --project backend pytest backend/tests/test_contracts.py -q` and observe collection/import failure because `intelamp.contracts` does not exist.
- [ ] **Step 3: Create package/config and minimal Pydantic contracts** with `extra="forbid"`, explicit enums, UTC datetime fields, and nullable provider-reported usage fields.
- [ ] **Step 4: Re-run the test file and require PASS.**
- [ ] **Step 5: Commit** `test+feat: define IntelAMP gateway contracts`.

## Task 2: SQLite durability and forward migration

**Files:** Create `backend/src/intelamp/database.py`, `backend/src/intelamp/models.py`, `backend/src/intelamp/repositories.py`, `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/versions/0001_initial.py`, `backend/tests/test_database.py`.

**Interfaces:** `create_engine_and_session(database_url)`, `SeatRepository`, `RunRepository`, `EventRepository`; event append returns monotonically increasing per-run `sequence`.

- [ ] **Step 1: Write failing tests** for WAL mode, seat CRUD/order persistence, run creation, monotonic event sequences, durable partial output, and prohibition on terminal transition from `stream_interrupted` to fabricated `completed` without an explicit new run.
- [ ] **Step 2: Run** the database tests and verify RED because repositories/tables do not exist.
- [ ] **Step 3: Implement SQLAlchemy models and repositories** for `seats`, `threads`, `turns`, `runs`, `run_events`; include `schema_version` columns and unique `(run_id, sequence)`.
- [ ] **Step 4: Implement Alembic migration 0001** with the same schema and enable `PRAGMA journal_mode=WAL` and foreign keys on connection.
- [ ] **Step 5: Run database tests and `alembic upgrade head` against a temporary SQLite file; require PASS.**
- [ ] **Step 6: Commit** `feat: add durable seat run and event storage`.

## Task 3: Provider registry and capability compiler

**Files:** Create `backend/src/intelamp/capabilities.py`, `backend/src/intelamp/registry.py`, `backend/src/intelamp/providers/base.py`, `backend/tests/test_capabilities.py`, `backend/tests/test_registry.py`, `config/providers.example.toml`.

**Interfaces:** `compile_capabilities(requested, offered) -> CapabilityCompileResult`; `ProviderRegistry.get(provider_id)`; registry owns per-provider `asyncio.Semaphore(max_concurrent_requests)`.

- [ ] **Step 1: Write failing tests** proving supported controls map, unsupported requested controls become hard incompatibilities when required, ignored optional controls become warnings, unknown never becomes supported, and registry rejects duplicate IDs/zero concurrency.
- [ ] **Step 2: Run tests and verify RED.**
- [ ] **Step 3: Implement capability compiler and provider registry** with typed four-state capability values and explicit provider metadata.
- [ ] **Step 4: Add example local llama provider** at `http://127.0.0.1:8080/v1` with no API key and `max_concurrent_requests = 1`.
- [ ] **Step 5: Run tests and require PASS.**
- [ ] **Step 6: Commit** `feat: add provider registry and capability compiler`.

## Task 4: Real OpenAI-compatible streaming adapter

**Files:** Create `backend/src/intelamp/providers/openai_compat.py`, `backend/tests/test_openai_compat.py`.

**Interfaces:** `OpenAICompatibleAdapter.list_models()`, `stream_chat(request, cancel_event) -> AsyncIterator[ProviderStreamEvent]`, `cancel()` through request cancellation/connection close when supported.

- [ ] **Step 1: Write failing parser tests** with recorded protocol fixtures for SSE `data:` chunks, `[DONE]`, usage payloads, malformed JSON, HTTP 429, timeout, and non-2xx protocol errors. Fixtures test parsing only; they are not acceptance evidence for provider integration.
- [ ] **Step 2: Run and verify RED.**
- [ ] **Step 3: Implement the adapter** using `httpx.AsyncClient.stream`, explicit timeout values, bearer header only when a secret is supplied by the server-side credential resolver, and typed failure mapping.
- [ ] **Step 4: Run parser/unit tests and require PASS.**
- [ ] **Step 5: Run a real local integration probe** against `http://127.0.0.1:8080/v1/models` and one short streaming `/chat/completions` request; record exact model identity and transcript under `evidence/` without secrets.
- [ ] **Step 6: Commit** `feat: stream real OpenAI compatible providers`.

## Task 5: Multi-seat dispatch lifecycle

**Files:** Create `backend/src/intelamp/dispatch.py`, `backend/tests/test_dispatch.py`.

**Interfaces:** `DispatchEngine.dispatch(request) -> DispatchAccepted`; `cancel(run_id)`; each run persists queued/running/chunk/terminal events and a receipt.

- [ ] **Step 1: Write failing tests** using an in-process deterministic test adapter for scheduler behavior only: provider semaphore cap, sibling failure isolation, user cancellation, partial-output preservation, retry lineage, and no automatic provider/model substitution.
- [ ] **Step 2: Run and verify RED.**
- [ ] **Step 3: Implement dispatch engine** with one task per ordinary seat, provider-owned semaphores, durable event append before publication, and terminal receipt finalization in `finally` paths.
- [ ] **Step 4: Run dispatch tests and require PASS.**
- [ ] **Step 5: Run a real two-seat local llama dispatch serially through its provider semaphore and verify both receipts exist with distinct run IDs and model identity.**
- [ ] **Step 6: Commit** `feat: add isolated multi-seat dispatch lifecycle`.

## Task 6: FastAPI API and resumable SSE

**Files:** Create `backend/src/intelamp/config.py`, `backend/src/intelamp/routes.py`, `backend/src/intelamp/app.py`, `backend/tests/test_routes.py`.

**Interfaces:** `GET /api/health`, `GET/POST/PATCH/DELETE /api/seats`, `GET /api/providers`, `POST /api/dispatch`, `GET /api/runs/{run_id}/events`, `POST /api/runs/{run_id}/cancel`, `GET /api/runs/{run_id}/receipt`.

- [ ] **Step 1: Write failing API tests** for seat CRUD, provider capability visibility, dispatch validation, SSE `id:` matching per-run sequence, `Last-Event-ID` resume, cancellation, and 404/typed failure responses.
- [ ] **Step 2: Run and verify RED.**
- [ ] **Step 3: Implement app/config/routes**; server loads provider TOML and resolves credential environment-variable names without storing secret values in SQLite or returning them from APIs.
- [ ] **Step 4: Run route tests and backend full suite.**
- [ ] **Step 5: Launch the gateway on loopback and prove `/api/health`, `/api/providers`, seat CRUD, and one real local llama dispatch over HTTP/SSE.**
- [ ] **Step 6: Commit** `feat: expose IntelAMP gateway API and resumable streams`.

## Task 7: Frontend foundation and sovereign design tokens

**Files:** Create frontend package/config files, `frontend/src/main.tsx`, `frontend/src/styles.css`, `frontend/src/components/AppShell.tsx`, `frontend/tests/seat-grid.test.tsx`.

**Interfaces:** App shell regions are left rail, top status, adaptive seat grid, composer, right inspector/sheet. NIGHT TABLE tokens are semantic CSS custom properties.

- [ ] **Step 1: Create test/build configuration only**, then write a failing rendering test requiring named shell regions, keyboard-accessible navigation, one-seat and six-seat layouts, and a mobile focused-seat selector.
- [ ] **Step 2: Run `npm test -- --run` and verify RED because production components do not exist.**
- [ ] **Step 3: Implement semantic tokens and shell/grid components** without gradients/glassmorphism; use CSS grid/container queries, `min-height:100dvh`, 44 px targets, 16 px mobile composer, focus-visible styling, and reduced-motion media query.
- [ ] **Step 4: Run tests and typecheck; require PASS.**
- [ ] **Step 5: Commit** `feat: add responsive IntelAMP operating shell`.

## Task 8: Typed API client and partitioned run store

**Files:** Create `frontend/src/api/types.ts`, `frontend/src/api/client.ts`, `frontend/src/state/runStore.ts`, `frontend/tests/api-client.test.ts`.

**Interfaces:** `IntelAmpClient` supports seat/provider CRUD/read, dispatch, per-run SSE subscription with resume ID, receipt retrieval, and cancel; `RunStore` updates only the addressed `run_id`.

- [ ] **Step 1: Write failing tests** for SSE parsing, resume ID propagation, typed cancellation, per-run immutable updates, and sibling state preservation.
- [ ] **Step 2: Run and verify RED.**
- [ ] **Step 3: Implement minimal API client and external-store style run state** so one seat token does not require replacing all sibling run objects.
- [ ] **Step 4: Run tests/typecheck and require PASS.**
- [ ] **Step 5: Commit** `feat: connect frontend to resumable run streams`.

## Task 9: Composer, seat panels, warnings, receipts

**Files:** Create/modify `frontend/src/components/Composer.tsx`, `SeatPanel.tsx`, `ProviderWarnings.tsx`, `Inspector.tsx`, `SeatGrid.tsx`, `frontend/tests/composer.test.tsx`.

**Interfaces:** Composer targets selected/all seats; dispatch is disabled on hard capability incompatibility; active-run Stop has at least equal prominence to Send; inspector exposes provider/model identity, context/capability digest placeholders only when real values exist, receipt state, timing source labels.

- [ ] **Step 1: Write failing interaction tests** for dispatch target selection, capability warning acknowledgement, stop/cancel, failed-seat isolation, and no cloud requirement when local provider is present.
- [ ] **Step 2: Run and verify RED.**
- [ ] **Step 3: Implement components** with explicit states (`queued`, `running`, `completed`, typed failure, `cancelled_by_user`) and no fake percentages/status dots.
- [ ] **Step 4: Run frontend suite/typecheck/build and require PASS.**
- [ ] **Step 5: Commit** `feat: add multi-seat composer and receipt inspector`.

## Task 10: Integration evidence, provenance guard, parity ledger

**Files:** Create `README.md`, `THIRD_PARTY.md`, `PARITY_LEDGER.md`, `scripts/dev.sh`, `evidence/README.md`; add acceptance tests/scripts without embedding credentials.

**Interfaces:** Docs state verified vs unverified integrations; parity entries use exactly `native`, `adapted`, `superior_replacement`, `intentionally_excluded`, `unverified`.

- [ ] **Step 1: Add provenance tests/checks** that fail on imports from a configured GPL reference path and scan committed source for forbidden copied headers/paths; document that this is a guard, not proof of legal cleanliness.
- [ ] **Step 2: Build the parity ledger** covering all capabilities named in the approved spec; Tranche 0 capabilities get witnesses, later capabilities remain `unverified` rather than marketing claims.
- [ ] **Step 3: Run full backend/frontend tests, migrations, typecheck and production build.**
- [ ] **Step 4: Run real local acceptance:** at least one seat, six configured seats through the local provider scheduler, cancel-in-flight, and one deliberately invalid provider seat alongside a successful local seat; save sanitized receipts/transcripts.
- [ ] **Step 5: Run the anti-slop firewall from the active skill pack against frontend source/build and record exact counts; manually record accessibility/attention checks that are not machine-verifiable.**
- [ ] **Step 6: Verify git diff/status, commit only intended files** as `feat: deliver IntelAMP tranche zero vertical slice` if a final integration commit is needed.

## Plan self-review

- Spec coverage for Tranche 0: repository/bootstrap, typed contracts, migrations, semantic design tokens, provider registry, OpenAI-compatible adapter, local llama.cpp, one/multi-seat streaming shell, durable receipts are all assigned to Tasks 1–10.
- Deferred by approved spec and therefore intentionally absent from production code here: Context Topology Matrix, branch DAG UI/merge behavior, False-Consensus Firewall, Replay, Tool Shadow, CAPT governed action, ChatHub/Open WebUI sidecars.
- No task may convert unit fixtures into real-integration evidence.
- No task may claim CAPT vessel identity for ordinary seat dispatch.
- No placeholder implementation language is permitted; any blocked real integration remains explicitly `UNVERIFIED` in the parity ledger.

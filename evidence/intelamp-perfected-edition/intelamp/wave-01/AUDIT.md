# IntelAMP AUDIT — Threads → Providers → Compose → Send → window.fetch → full suite

Audit window: 2026-09-17 → 2026-09-18 (CDT). Operator-directed pivot from the frozen
QIPC stage (vNEXT-3 stays frozen; no Wave 4; no global QIPC convergence).
Evidence rule in force: direct tool/runtime observations only; agent/reference output
untrusted until independently reproduced. This audit's claims are single-operator,
self-verified (one author wrote the fixes and ran the checks).

## Order executed (operator order, one re-sequencing documented)

The operator's order listed `window.fetch` fifth. Live reproduction on 2026-09-17 showed it was
an **upstream prerequisite** — one root cause explaining all four prior items at once — so it was
repaired first, with the re-sequencing recorded:

1. **window.fetch (re-sequenced to first)** — real defect.
   - Live pre-fix (real browser): app mounts; nav renders; then
     `Failed to execute 'fetch' on 'Window': Illegal invocation` rendered into the app's own
     `role="alert"`; seat grid `empty|0`; every gateway call throwing.
   - Root cause: `client.ts` held `fetchImpl = fetch` and invoked it as `this.fetchImpl(...)`;
     `fetch` is a WebIDL operation on Window and a detached receiver throws.
   - Fix: `resolveFetch()` in `frontend/src/api/client.ts` binds the implicit global to
     `globalThis`; explicitly injected `fetchImpl` is honoured as-is (tests unaffected).
   - Verified: typecheck 0; vitest 14 passed; **live browser post-fix: `GATEWAY_ERROR: []`,
     seat grid `single|1`, real provider data rendered**.

2. **Send** — blocked by (1); after the fix, **verified end-to-end live**:
   composer → client → `/api/dispatch` → DispatchEngine → openai_compat adapter → local
   provider :8080 → SSE → seat text → receipt `run_0ab60c045fc049ba8f4f85bbf69c6284`,
   text `PONG`, real request/context/output digests, 61 in / 33 out tokens, no failure class.

3. **Compose** — blocked by (1); textarea verified controlled (real input persisted),
   targets render from live seats. No independent defect found.

4. **Providers** — data was always served (`/api/providers` → real `local-llama`); blocked by (1);
   renders after the fix. No independent defect found.

5. **Threads** — honest disposition: **not implemented** at audit open (`/api/threads` HTTP 404,
   no thread methods in the client, `thread_id` hardcoded to `thread_local_default` at
   `AppShell.tsx:69`, nav button was a focus-mover). Operator authorized the vertical slice ("4").
   Implemented and verified:
   - `contracts.py`: `ThreadCreate`, `ThreadRecord` (created_at, run_count, last_run_at).
   - `models.py`: `ThreadModel.created_at` added; `migrations/versions/0002_thread_created_at.py`
     (nullable add + explicit backfill; SQLite rejects CURRENT_TIMESTAMP as an ADD COLUMN default).
   - `repositories.py`: `ThreadRepository.create/get/list` — the listing **unions explicit thread
     rows with distinct `runs.thread_id`** so no run is invisible; `runs.thread_id` has no FK in the
     live schema (verified: plain `VARCHAR NOT NULL`), so no integrity backfill was needed.
   - `routes.py`: `GET /api/threads` (200), `POST /api/threads` (201), `GET /api/threads/{id}`
     (404 `thread_not_found`); `RouteServices.threads` wired in `app.py`.
   - Frontend: `client.ts` thread methods; `AppShell` thread state + selector + "New thread" +
     dispatch carrying the selected `thread_id` (hardcoded default removed); honest fallback
     (auto-creates a thread when none is selected); styles for the thread control.
   - Verified live: `/api/threads` 200 with both threads + run_count; "New thread" created
     `thread_f9dd2ff0417e4db8945ba61b81dff4a8` and dispatch carried it into the run receipt.

## Additional defect found and repaired (SSE silent-break race)

Observed live: a seat stayed `running` for 30 s while its receipt recorded a failure 24 ms after
start. Root cause path: `dispatch.finalize()` commits terminal state BEFORE the terminal event is
appended, and the events stream broke **silently** when it saw an empty batch on an
already-terminal run — a subscriber polling inside that window never learned the outcome.

- Falsifier written and executed: `test_stream_delivers_terminal_when_terminal_event_was_never_appended`
  → **FAILED exactly as predicted** (`Response [200 OK]` with empty body).
- Repair: the stream loop now reconstructs a terminal frame from durable receipt state, marked
  `reconstructed: true` — it never invents a terminal state, it reports the state the run has.
- Verified: backend **40 passed**; live replay of the repaired server; **live browser: terminal
  reaches the UI (`SEEN_TERMINAL_IN_UI: true`, `FAILURE_SHOWN: provider_unavailable`, receipt present)**.

## Full verification suite (final state)

| check | result |
| --- | --- |
| `uv run --project backend pytest backend/tests -q` | **40 passed** (39 baseline + 1 new falsifier) |
| `npm --prefix frontend test -- --run` | **14 passed** |
| `npm --prefix frontend run typecheck` | **exit 0** |
| `npm --prefix frontend run build` | **exit 0** (35 modules) |
| `./scripts/provenance_guard.py backend/src frontend/src` | **PASS issues=0** |
| real backend startup + health | `/api/health` → `{"status":"ok"}` (verified across 3 restarts) |
| SSE | all 3 events delivered promptly (fresh + resumed); reconstructed terminal verified live |
| real provider success path | verified 2026-09-17 (`run_0ab60c…`, PONG); **provider :8080 down at audit close** (4 consecutive checks) |

## Environment footgun repaired (migration landed on the wrong DB)

`alembic.ini`'s default URL is cwd-relative (`sqlite+aiosqlite:///./intelamp.sqlite3`); alembic must
run from `backend/` (relative `script_location`), so migration `0002` landed on
`backend/intelamp.sqlite3` while the live repo-root DB stayed at `0001_initial` (both verified
read-only). Fix: `env.py` now resolves relative sqlite paths against the repo root; `0002` re-run on
the live DB and verified (alembic `0002_thread_created_at`, threads = 4 columns).

## Honest failure semantics observed (not defects)

- Provider down at dispatch → `terminal_state=failed`, `failure_class=provider_unavailable`,
  `output_digest=sha256:e3b0c442…` (the empty-string digest), typed failure surfaced in the UI.
- One run (`run_1a2…`) received its terminal event late-but-persisted; the unit falsifier covers the
  true never-appended window.

## Git state

`main` @ 708e2d2 + 11 modified files + 1 new migration + `evidence/` untracked (list in RUN_MANIFEST).
No commits made by this session unless the operator asks.

## Unresolved / UNPROVEN

- U1. Success-path Send re-run blocked by provider :8080 being down (external service; operator-owned).
- U2. The SSE race repair's `reconstructed` frame path is unit-verified + live-verified once; not
  independently reproduced.
- U3. All results single-operator/self-verified; no independent reproduction (standing condition of
  the frozen QIPC stage).
- U4. Ledger anchors: cp-cmd-hermes-b0ec44cf0af8 (IntelAMP audit milestone) plus the four earlier
  QIPC/tooling anchors — all verified read-only at global_sequence 4382.
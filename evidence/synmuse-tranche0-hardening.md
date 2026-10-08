# SynMuse Tranche 0 hardening — evidence note

Date: 2026-10-08 (CDT). Author: SynMuse (Inversion Labs), on branch
`synmuse/tranche-0-hardening` over HEAD `9d5e3f0`. Labels follow the repo's
discipline: VERIFIED means reproduced by execution in this session.

## Changes

1. `LICENSE` added (MIT, Copyright (c) 2026 Inversion Labs). The repo
   previously shipped no license while documenting third-party licenses
   carefully.
2. Receipt dead fields resolved:
   - `provider_request_id` is populated end-to-end: the OpenAI-compatible
     adapter captures the chunk `id` (or `x-request-id` header fallback),
     carries it on the DONE stream event, dispatch persists it at finalize,
     and the receipt already exposed the field.
   - `estimated_cost` removed from the receipt contract, the HTTP receipt
     mapping, the frontend type, and a frontend test fixture. The database
     column remains (unread) for schema compatibility; no pricing was
     invented to fill it.
3. Failure logging: `intelamp.dispatch` now logs provider failure classes
   (warning, with provider/model) and logs full tracebacks for
   `FailureClass.UNKNOWN` (error). Previously the backend had no logging
   at all, so the UNKNOWN class left no diagnostic trace.
4. Bounded per-seat context assembly (the tranche-0 gap: seats previously
   received only the bare prompt):
   - Migration `0003_run_prompt` adds nullable `runs.prompt`.
   - Dispatch persists the prompt and assembles, per seat, that seat's own
     prior completed exchanges in the thread (reconstructed from chunk
     events), bounded to 20 runs / 24k chars, whole exchanges only.
   - The run's `context_view_digest` is now taken over the exact message
     list sent, so a receipt proves what context the provider received.
   - A `context_assembled` run event records history_runs/message_count
     when history was included. Failed/cancelled runs and other seats'
     histories never enter context.

## Verification (all VERIFIED this session)

- Backend: `pytest backend/tests -q` → **45 passed** (40 pre-existing,
  5 new: seat-history, cross-seat/failed exclusion, provider_request_id
  persistence, UNKNOWN-failure logging, DONE request-id capture).
  Note: in the sandbox, one pre-existing test fails if `NO_PROXY`
  contains bracketed IPv6 entries (httpx client construction); with a
  sanitized `NO_PROXY` the suite is clean. This is an environment trait,
  recorded here so it is not misread as a repo defect.
- Frontend: `npm test -- --run` → **14 passed**; `npm run typecheck` →
  clean (one fixture referenced the removed `estimated_cost` and was
  updated); `npm run build` → succeeds.
- Provenance: `./scripts/provenance_guard.py backend/src frontend/src`
  → PASS, issues=0.
- Migrations: fresh SQLite `alembic upgrade head` runs 0001 → 0002 →
  0003; `runs.prompt` present.

## Still UNVERIFIED / unchanged

- Remote (cloud) providers: only the local OpenAI-compatible path plus
  mock-transport fixtures exercised; no remote acceptance recorded.
- Live llama.cpp acceptance was NOT re-run this session; context assembly
  is verified against scripted adapters and unit fixtures.
- `evidence_root_digest` still hashes a `none:not-selected` stand-in and
  `tool_policy_digest` still hashes an identifier; context digests are
  now content-true, the other two remain identifier-true only.

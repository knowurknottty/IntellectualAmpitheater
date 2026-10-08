# SynMuse Tier-1 features + Mirage Lint — evidence note

Date: 2026-10-08 (CDT). Branch `synmuse/tranche-0-hardening`. Built in the
order Kirk set: 4 → 1 → 3 → 2, then 5 (Mirage Lint) as first Tier 2.
Labels: VERIFIED = reproduced by execution this session.

## Feature 4 — "What it saw" (commit 5ee975b)
- `runs.context_messages` (migration 0004) stores the exact message list.
- `GET /api/runs/{id}/context` serves the persisted list; Inspector renders
  role/content verbatim. Legacy runs report messages=null, never a rebuild.
- VERIFIED: stored list equals the scripted adapter's received list
  (test_dispatch), endpoint shape + 404 (test_routes).

## Feature 1 — Effective Voices (commit aadfd8f)
- `voices.compute_effective_voices` clusters completed runs of a dispatch
  by (model, exact context); `GET /api/threads/{id}/effective-voices`;
  header shows "N effective voices".
- VERIFIED incl. falsifier: same model under two provider aliases with the
  same context collapses to one voice; unrecorded context never merges.

## Feature 3 — Counterfactual Seat (commit b093c32)
- `POST /api/runs/{id}/replay`: exactly one variable (model_id, prompt, or
  one generation field), must differ; 422 otherwise.
- Replay context is cut at the source run (its own answer never leaks in);
  a model-only replay reproduces the source's `context_view_digest`.
- The new tests caught a real race: post-hoc event appends from the route
  raced the run task's own appends (UNIQUE run_id+sequence). Fixed by
  appending lineage events synchronously inside dispatch, pre-task.
  Suite run 3× consecutively to check for flake: 54/54 each time.

## Feature 2 — Sealed Reveal + Anchoring Delta (commit e48c393)
- `POST /api/dispatch/{id}/reveal` (one per dispatch, 409 on repeat;
  requires ≥2 completed seats); reveal runs are `run_kind=reveal`
  (migration 0005) and are excluded from conversation history.
- `GET /api/dispatch/{id}/anchoring`: per-seat lexical movement toward
  peers before/after reveal, labeled exploratory.
- VERIFIED: holding seat delta 0.0 / self-similarity 1.0; copying seat
  delta positive with toward-after 1.0 (tests). Early expectation in one
  test was miscalibrated (shared word "answer" inflates baseline
  similarity); test fixed, math unchanged — recorded honestly.

## Feature 5 — Consensus Mirage Lint (this commit)
- `mirage.mirage_lint` over the latest dispatch: verdicts `mirage_risk` /
  `no_mirage_signal` / `insufficient_data`; advisory only.
- VERIFIED: duplicated-model agreement trips it; independent models
  agreeing does not; two-seat panels are insufficient data.

## Full verification (this session, final tree)
- Backend: **64 passed** (`pytest backend/tests -q`).
- Frontend: **14 passed**, typecheck clean, production build succeeds.
- Provenance guard: PASS, issues=0.
- Migrations on a fresh DB: 0001 → 0005 clean; runs carry prompt,
  context_messages, run_kind, source_run_id.

## Still UNVERIFIED
- Live-provider acceptance of the new endpoints (scripted adapters and
  mock transports only); remote providers remain unverified per ledger.
- Similarity is lexical (difflib). Semantic clustering is future work and
  every surface using it is labeled exploratory.
- Anchoring Delta measures movement, not correctness or sycophancy.

# INTELAMP — INVERSION LABS PERFECTED EDITION — SDR

Status: CORE AUDIT + QIPC STAGE COMPLETE; FULL COMPLETION NOT CLAIMED.
Written 2026-09-18 (CDT). All claims below are single-operator, self-verified unless marked
UNVERIFIED. Agent/reference output from the MOA waves was rejected as evidence (fabricated or
tool-blind); nothing in this document relies on it.

Label discipline (never interchangeable):
- OBSERVED — seen by direct tool/runtime observation.
- CHANGED — modified by this session, verified.
- VERIFIED — reproduced by execution or live operation.
- UNPROVEN — believed but not independently established.

## 1. Technical thesis

A multi-model workbench is trustworthy only when (a) one root cause cannot make four surfaces
appear broken, (b) failure semantics are typed and preserved, (c) correlated answers are never
laundered into consensus, and (d) every claim is traceable to executed evidence. This session
validated (a)–(d) by repair: the `window.fetch` receiver fault knocked out Threads/Providers/
Compose/Send at once; the SSE silent-break race hid terminal outcomes from live subscribers; and
the frozen QIPC stage now carries a falsifier-tested convergence mechanism with provenance-keyed
correlation clustering.

## 2. Final architecture (as it stands at HEAD 186b4e5)

- FastAPI gateway (backend/src/intelamp): contracts, capability compiler, dispatch engine,
  provider registry + openai_compat adapter, repositories, routes.
- SQLite (WAL) persistence: seats, threads, turns, runs, ordered run_events; migrations via
  Alembic (0001_initial → 0002_thread_created_at).
- React/TypeScript/Vite shell: AppShell (nav, thread control, seat grid, composer, inspector),
  capability-loss acknowledgement, Stop, receipt inspector.
- Verified live flows: dispatch → SSE (fresh, resumed via Last-Event-ID, reconstructed-terminal)
  → receipt; thread listing/creation/selection carried into dispatch.

## 3. QIPC-HYBRID-vNEXT-3 (frozen by operator directive; no Wave 4, no global convergence)

State/belief/evidence representation: probability vectors over an enumerated candidate set plus a
residual `__open__`; provenance tuple π per source; reliability r with a closed calibration loop.
Update: deterministic reliability-weighted log-linear pooling over enumerated hypotheses only
(partial-information: absent = no opinion), equal-split within a provenance cluster
(w_i = min(1, r_i/k_c)), residual applied post-hoc as a calibration floor (P_RESIDUAL=0.05).
Quarantine: malformed posteriors only (fail-closed); valid-but-extreme sources reported as
`outliers` and kept. Dissent always reported. Fusion is stateless/one-shot.
Reference implementation: `qipc/wave-02/experiments/qipc_hybrid.py` + wave-03 `qipc_hybrid_v3.py`.
Falsifier suites F1–F15: **14/14 graded pass, F13 informational** (self-verified; single author).
Full spec: `qipc/wave-03/CANONICAL.md`.

## 4. Waves used

- QIPC Wave 1 — discovery + falsification of the canonical lineage (E1–E6 receipts).
- QIPC Wave 2 — implementation + F1–F8/F9–F13; three defects repaired.
- QIPC Wave 3 — θ false-positive repaired (honest dissent kept), residual-as-floor, spurious-F2
  disclosure; F14/F15 added.
- IntelAMP audit wave — mandated order executed with one documented re-sequencing.
No cohort waves completed independently: 0/66 usable vessels across three waves; two slots
fabricated tool output (recorded, rejected as validation).

## 5. Cohort/model identities + accounting

- Aggregators (successive): openrouter:deepseek/deepseek-v4.1-flash (qd1→qd2), then
  z-ai/glm-5.3-flash (Nvidia, current).
- Cohort slots by wave — W1: inversion-labs-deep-seekv4-flash-0713-gen-purp,
  capt-vessel-kernel-council-scale-deliberation, capt-forge-engineering-and-repository-specialist;
  W2: inversionlabs-step3-7flash, inversion-labs-mimo2-5 (degenerate), inversiolabs-hy3;
  W3: stealth/union-alpha, deepseek/deepseek-v4-flash-0731 (fabricated),
  z-ai/glm-5.3-flash (fabricated).
- Logical vessels: 66/wave requested → 0 completed, 0 failed, 63 starved, 3 invalidated per wave.
- Physical provider calls: 3 cohort + 1 aggregator per wave; vessel-level calls: 0.

## 6. Defects discovered (all OBSERVED, then VERIFIED fixed unless noted)

| id | defect | evidence | status |
| --- | --- | --- | --- |
| IA-D1 | `window.fetch` Illegal invocation — one root cause killed Threads/Providers/Compose/Send | live browser pre/post-fix | FIXED, VERIFIED live |
| IA-D2 | SSE silent-break race — terminal outcome hidden from a subscriber in the finalize→append window | falsifier FAILED as predicted; live UI stuck `running` 30s | FIXED, VERIFIED (unit + live) |
| IA-D3 | Threads not implemented (404, hardcoded thread_id, decorative nav) | live curl + source | SLICE IMPLEMENTED, VERIFIED live |
| IA-D4 | Migration cwd-relative footgun (0002 landed on backend/intelamp.sqlite3) | both DBs read-only | FIXED, VERIFIED |
| IA-D5 | Wave-02 F2 pass spurious (both sources quarantined) | exposed by W3-C1 repair | DISCLOSED, superseded |
| Q-D1..D15 | Lineage defects (non-reproducibility, destructive interference, decoupled agreement metric, unbounded influence, false zero-stubs, vacuous tests, …) | qipc/wave-01/experiments/receipts.json; COHORT-DISCOVERY §3 | repaired/superseded in vNEXT-3 |

## 7. Changes implemented

51 files, +4011/−16, commit `186b4e55fa780338013348f8ae1a9b4f3aae2432` on `main` (parent `708e2d2`).
Highlights: `resolveFetch()` (client.ts); Threads slice (contracts/models/migration 0002/
repositories/routes/AppShell/types/styles); SSE reconstructed-terminal frame (routes.py);
env.py repo-root DB resolution; new falsifier test; evidence/ tree committed.

## 8. Removed mechanisms

Complex-amplitude interference; measurement/collapse; "Ricci flow"; VQE/qiskit; qasm;
fabricated gate confidence (0.75); sqrt(count) downweight; the ρ-parameterization; the iterative
round loop; exclusion-by-disagreement (θ quarantine); residual-as-competitor; hardcoded
`thread_local_default` dispatch.

## 9. Accepted innovations (novelty bar applied)

- Provenance-keyed correlation clustering (shares IntelAMP's structural lineage) — mechanism,
  causal story, baseline (no prior variant models shared provenance), falsifier (F3/F9/F10), cost.
- Reconstructed-terminal frame marked `reconstructed: true` — never invents state; falsified the
  silent-break; verified live.
- Partial-information pooling (absence = no opinion) + residual-as-calibration-floor.
- Implicit-thread surfacing (no run ever invisible; no FK backfill needed — verified).

## 10. Rejected innovations

Sybil resistance (declared non-guarantee — fabricated distinct keys defeat clustering; no honest
mechanism proposed); numeric "independent vote equivalents"; quantum terminology as branding;
196-vessel/198-vessel consensus claims (evidence supports single-author/self-verified 14/14).

## 11. Security boundaries

Browser never receives provider secrets (verified: `/api/providers` serializes capabilities only);
ledger token never printed; SQLite writes to the runtime DB forbidden (read-only copies used for
verification); gateway validates seats/inputs; operator-owned services (Actual daemon, miner
config, relay) never killed or disabled to force a test through; QIPC remains advisory-only.

## 12. Model/provider semantics

No silent substitution: aggregator identity recorded at every step; OpenAI models only via the
user-visible ChatGPT route (none used); provider failure classes typed (503→provider_protocol_error,
429→provider_rate_limited, absent→provider_unavailable — all verified live).

## 13. Persistence/state architecture

SQLite WAL at repo root (migrations land there after the env.py fix); per-run event sequences with
unique constraint; receipt digests (request/context/evidence/tool policy/output); retry lineage
column; reconstructed terminal marked in-band. Verify after any write by reading back the exact
target.

## 14. Failure/recovery model

Typed failure classes (14); partial output preserved (output_digest of the empty string observed
and correct); interrupted streams not rewritten as completed; one seat's failure never erases
siblings; backend restarts (3) verified; cancellation verified by unit test and route.

## 15. Human-first UX

Extraction 0; OPERATE surface; 44px controls; visible focus; reduced-motion CSS; honest empty
states; capability-loss acknowledgement; Stop as prominent as Send while active; thread control
styled to the existing NIGHT TABLE system. No redesign for its own sake.

## 16. Provenance/evidence

Evidence tree committed: `evidence/intelamp-perfected-edition/` (RUN_MANIFEST.md; qipc/wave-01..03
with experiments + receipts; intelamp/wave-01/AUDIT.md; handoffs 01–03; verification/ transcripts).
Ledger anchors (all verified read-only @4382): cp-cmd-hermes-3493bebb2835, -b4c73c79357a,
-bef2df81ce7d, -39a536fd8f5e, -b0ec44cf0af8, -131a3ee79b34, -4b030bb1877c.

## 17. Verification matrix

| check | result |
| --- | --- |
| `uv run --project backend pytest backend/tests -q` | 40 passed |
| `npm --prefix frontend test -- --run` | 14 passed |
| `npm --prefix frontend run typecheck` | exit 0 |
| `npm --prefix frontend run build` | exit 0 (35 modules) |
| `./scripts/provenance_guard.py backend/src frontend/src` | PASS issues=0 |
| fresh DB migrations | 0001 → 0002 verified (live + temp copies) |
| real backend startup + health | ok across 3 restarts |
| SSE fresh/resumed/reconstructed | verified live + unit |
| cancellation | verified (unit + route) |
| real provider success | run_0ab60c… (PONG, 61/33 tokens) |
| live UI operation | Threads, Providers, Compose, Send, receipts, capability-loss, failure states — all exercised in a real browser |

## 18. Measured performance

Provider streaming measured: first deltas within ~1s of dispatch on the success path; failed runs
terminal within 24ms (provider absent); fusion O(S·|H|)+O(S log S) (trivial at panel sizes).
No benchmark suite was run; no benchmark claims are made.

## 19. Unresolved risks

- U1: success-path Send re-run blocked at audit close by the node's capacity policy (429
  node_saturated; `actual stats` shows 0 active/0 queued — policy-reserved). Operator-owned; not bypassed.
- U2: all results single-operator/self-verified; no independent reproduction exists (standing
  condition of the frozen QIPC stage).
- U3: Sybil resistance absent (declared).
- U4: parameters (P_RESIDUAL, R_UNCAL, W_MAX, ε, θ, N_CAL) falsifier-constrained, not derived.
- U5: prior-art status of belief-distribution consensus not adjudicated (patent overclaim stands).

## 20. Deferred work

- Global QIPC convergence (`qipc/QIPC-HYBRID-vNEXT-FINAL.md`) — reserved for the operator's
  explicit final-trio signal.
- IntelAMP tranches 2–4 (replay lab, tool shadow, CAPT authority adapter, ecosystem parity) —
  per the parity ledger; not started.
- Independent (non-self) verification of F1–F15 and the audit claims.

## 21. Exact git state

`main` @ `186b4e55fa780338013348f8ae1a9b4f3aae2432` (parent `708e2d2`); working tree clean;
gitignore covers `/intelamp.sqlite3`, `-shm`, `-wal`, `backend/*.sqlite3`, `frontend/dist/`.

Completion state: CORE MISSION VERIFIED (audit + QIPC stage, within their scopes);
EXPERIMENTAL ITEMS REMAIN UNPROVEN. Full completion is not claimed.

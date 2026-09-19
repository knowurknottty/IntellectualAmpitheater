# RUN_MANIFEST — INTELAMP PERFECTED EDITION

mission_id: INTELAMP-PERFECTED-EDITION
opened: 2026-09-17 (CDT)
operator: Inversion Labs founder (human)
acting model / aggregator: openrouter:deepseek/deepseek-v4.1-flash (preset qd1, Hermes "moa")
concurrency ceiling: 3 cohort-agents per active MOA wave (enforced)
logical vessels per cohort-agent: 22 (semantic; NOT 22 physical provider calls)
logical perspectives per wave: 66

## Current position

current_wave: 3 — QIPC FROZEN BY OPERATOR DIRECTIVE (2026-09-17)
stage: INTELAMP REPOSITORY/RUNTIME AUDIT (pivot authorized)
terminal_state: AUDIT_IN_PROGRESS — order Threads -> Providers -> Compose -> Send -> window.fetch -> full verification suite
operator_directives_in_force:
  - QIPC-HYBRID-vNEXT-3 frozen exactly where it is; NO Wave 4; NO global QIPC convergence
  - the three cohort waves are NOT independent validation (0/66 usable vessels; two slots fabricated tool output)
  - evidence status: single-author / self-verified 14/14 (F1-F15), NOT 198-vessel consensus
  - evidence = direct tool/runtime observations only; agent/reference output untrusted until independently reproduced
  - no new ledger checkpoint until a real repair/verification milestone occurs
repo_under_future_mission: /Users/knowurknot/capt-node-workspace/IntellectualAmpitheater
repo_head_at_wave_open: 708e2d2172605cec214ece924ff167f454dcc490 (branch main)

## CAPT ledger anchors (durable handle — the ledger proves THAT/WHEN, not WHAT)

Runtime observed 2026-09-17: socket alive, pid alive, integrity ok,
head=4382, chain=sha256:1a12bef056c7a3a338f915f3c7d3a93ebb307eb1b8aad2b03f7296da3599ea83.
Memory policy v1, triggerIntervalTokens=32768.

| checkpoint id | milestone | global_sequence | verified read-only |
| --- | --- | --- | --- |
| cp-cmd-hermes-3493bebb2835 | QIPC Wave 1 complete (canonical + E1–E6 receipts) | 4382 | yes |
| cp-cmd-hermes-b4c73c79357a | QIPC Wave 2 complete (vNEXT-2 + F1–F13) | 4382 | yes |
| cp-cmd-hermes-bef2df81ce7d | capt-ledger-context script repair (timeline/recover crash) | 4382 | yes |
| cp-cmd-hermes-39a536fd8f5e | QIPC Wave 3 complete (vNEXT-3 + F1–F15, 14/14 graded) | 4382 | yes |

Ledger tooling repair (CAPT dogfooding): `~/.hermes/skills/capt/capt-ledger-context/scripts/capt_ledger.py`
v1.0.0 crashed in `timeline` and `recover` (`AttributeError: 'NoneType' object has no attribute 'get'`).
Root cause, observed on the wire: the op `event_timeline` is unsupported by this runtime and returns
NO reply frame (socket then closed), while other unknown ops return a clean
`{"ok": false, "error": "unknown op ..."}` envelope. Repaired with `_safe_result()` guard +
fail-soft `_timeline()` + graceful `recover` degradation; verified. There is no global event-timeline
query op on this runtime; use `events <stream_id> [n]`.

## Wave ledger

### Wave 0 (pre-wave, bootstrap)

- No prior mission directory existed; `evidence/intelamp-perfected-edition/` was created this session.
- Confirmed absent: any `RUN_MANIFEST.md`, `qipc/`, `handoffs/`, `verification/` from earlier waves.

### Wave 1 — QIPC

- wave_number: 1
- status: artifacts written; STOPPED for manual agent swap
- repository HEAD at wave start: IntellectualAmpitheater @ 708e2d2; QIPC lineage @ biocapt-ecosystem e810bca
- aggregator identity (observed): openrouter:deepseek/deepseek-v4.1-flash
- aggregator requested by mission (intended): openrouter:deepseek/deepseek-v4.1-flash → MATCH (no substitution)

#### Cohort-agent identities (the 3 references in this MOA wave)

| slot | identity | tool surface | usable independent artifact? |
| --- | --- | --- | --- |
| C1 | openrouter:@preset/inversion-labs-deep-seekv4-flash-0713-gen-purp | web search/fetch only (NO filesystem, NO shell, NO git) | no — tool-boundary statement + null findings |
| C2 | openrouter:@preset/capt-vessel-kernel-council-scale-deliberation | web search only | no — truncated-packet null result + source-quality flag |
| C3 | openrouter:@preset/capt-forge-engineering-and-repository-specialist | web search only | no — framing refusal + entity-verification, no task execution |

Hard structural finding: all three cohort-agents ran blind AND tool-blind. None could read the repository, the QIPC sources, or write artifacts. This is recorded as the wave's dominant failure mode, not hidden.

#### Vessel accounting (logical)

| cohort | requested vessels | completed | failed | starved | invalidated |
| --- | --- | --- | --- | --- | --- |
| C1 | 22 | 0 | 0 | 21 | 1 (the cohort's own identity/authority dispute → invalidated as a task artifact) |
| C2 | 22 | 0 | 0 | 21 | 1 (packet truncation → invalidated as a task artifact) |
| C3 | 22 | 0 | 0 | 21 | 1 (framing refusal → invalidated as a task artifact) |
| TOTAL (mission-defined 3x22) | 66 | 0 | 0 | 63 | 3 |

Aggregator authority pass (recorded separately, NOT counted as cohort independence):

- AGG-22: 22 QIPC error-seeking lenses applied by the tool-capable aggregator → 22/22 completed, evidence = executed experiments `qipc/wave-01/experiments/` + lineage inspection.
- Independence claim: NONE. This is single-model work. Correlated-error risk is maximal. It substitutes for, and must NOT be reported as, three independent cohorts.

#### Provider-call accounting (observable)

- Cohort-agent physical calls: 3 (the three reference completions delivered by the MOA layer).
- Aggregator physical calls: 1 acting stream (this session).
- Vessel-level physical calls: 0. Logical vessels 66 (mission) + 22 (aggregator lenses) were NOT expanded into 66+ provider calls, per the mission's explicit instruction and the orchestration invariant.

#### Artifacts produced this wave

- qipc/wave-01/VESSELS.md
- qipc/wave-01/COHORT-DISCOVERY.md
- qipc/wave-01/RECURSION-5X.md
- qipc/wave-01/WAVE-CONVERGENCE.md
- qipc/wave-01/POST-CONVERGENCE-5X.md
- qipc/wave-01/CANONICAL.md
- qipc/wave-01/experiments/qipc_falsifier.py
- qipc/wave-01/experiments/receipts.json
- handoffs/QIPC-WAVE-01-HANDOFF.md
- RUN_MANIFEST.md (this file)

#### Unresolved findings (carried forward)

- U1. No independent corroboration exists for any Wave-1 QIPC claim (all three cohorts tool-blind).
- U2. QIPC-HYBRID-vNEXT is proposed, not yet implemented or falsified outside this harness.
- U3. The IntelAMP repository was inspected only for provenance this wave; its capability/UI claims are NOT yet reproduced. (Deferred to IntelAMP waves.)
- U4. Whether the mission's intended aggregator preset actually resolved to the same weights as the aggregator id is not externally observable from here; identity is taken from the runtime header.

#### Rejected findings

- R1. (C2) "IntelAMP / Inversion Labs / QIPC do not exist" — REJECTED. The entities exist as local repositories on this host (verified by direct filesystem read). Absence of a public web footprint is not absence of the entity.
- R2. (C2) the "QRBT / Rq" thesis source — REJECTED as evidence (unverifiable precise benchmarks); recorded only as a source-quality warning.

#### Pending experiments

- P1. Implement QIPC-HYBRID-vNEXT and rerun the E1–E6 falsifier against it.
- P2. Extend the falsifier with the cluster-discount test (two sources sharing an evidence root must not sharpen the posterior).

#### Wave handoff

- handoffs/QIPC-WAVE-01-HANDOFF.md

---

### Wave 2 — QIPC (adversarial challenge of the Wave-01 canonical)

- wave_number: 2
- status: artifacts written; implementation executed; STOPPED for manual agent swap
- opened by: operator "cont" after the qd1 -> qd2 model swap (accepted as the manual agent swap)
- repository HEAD: IntellectualAmpitheater @ 708e2d2 (unchanged); QIPC lineage @ biocapt-ecosystem e810bca
- aggregator identity (observed): openrouter:deepseek/deepseek-v4.1-flash (qd2); no substitution

#### Cohort-agent identities

| slot | identity | usable independent artifact? |
| --- | --- | --- |
| C1 | openrouter:@preset/inversionlabs-step3-7flash | no — coherent, non-executing, tool-blind |
| C2 | openrouter:@preset/inversion-labs-mimo2-5 | no — DEGENERATE OUTPUT (incoherent token salad; zero recoverable propositions) |
| C3 | openrouter:@preset/inversiolabs-hy3 | no — coherent, non-executing, tool-blind; agreed with the mandated next action |

#### Vessel accounting (logical)

| cohort | requested | completed | failed | starved | invalidated |
| --- | --- | --- | --- | --- | --- |
| C1 | 22 | 0 | 0 | 21 | 1 |
| C2 | 22 | 0 | 0 | 21 | 1 |
| C3 | 22 | 0 | 0 | 21 | 1 |
| TOTAL | 66 | 0 | 0 | 63 | 3 |

Aggregator AGG-22 lens pass: 22/22 completed — NOT counted as cohort independence.

#### Provider-call accounting (observable)

- Cohort-agent physical calls: 3. Aggregator: 1 acting stream. Vessel-level calls: 0.

#### What was actually produced

- Implemented the Wave-01 canonical: `qipc/wave-02/experiments/qipc_hybrid.py`.
- Falsifier suites executed: `qipc_hybrid_falsifier.py` (F1–F8, 8/8 pass), `qipc_hybrid_falsifier_ext.py` (F9–F12 pass; F13 informational).
- Three defects found by the falsifiers and repaired (partial-information pooling; support-restricted quarantine; residual open-world prior). Recorded in `qipc/wave-02/COHORT-DISCOVERY.md`.
- Key verified result: 5 correlated sources (one provenance key) vs 2 independent sources → the independent minority wins (F9).

#### Artifacts produced this wave

- qipc/wave-02/COHORT-DISCOVERY.md
- qipc/wave-02/RECURSION-5X.md
- qipc/wave-02/WAVE-CONVERGENCE.md
- qipc/wave-02/POST-CONVERGENCE-5X.md
- qipc/wave-02/CANONICAL.md
- qipc/wave-02/experiments/qipc_hybrid.py
- qipc/wave-02/experiments/qipc_hybrid_falsifier.py
- qipc/wave-02/experiments/qipc_hybrid_falsifier_ext.py
- qipc/wave-02/experiments/f1_8.json, f9_13.json
- handoffs/QIPC-WAVE-02-HANDOFF.md

#### Unresolved findings (carried forward)

- U1. No independent corroboration of any Wave-2 finding (63/66 mission vessels starved; implementation + tests share one author).
- U2. LINEAGE_UNKNOWN is declared but enforced nowhere — the strongest remaining attack surface.
- U3. No Sybil resistance (declared non-guarantee).
- U4. Parameters (P_RESIDUAL, R_UNCAL, W_MAX, ε, θ, N_CAL) falsifier-constrained, not derived.
- U5. Prior-art status of belief-distribution consensus not adjudicated.

#### Rejected findings

- R1. (C2) degenerate output — rejected as content; preserved as a provider/preset quality artifact.
- R2. Any implication that three blind cohorts constitute independent corroboration — rejected; they produced no technical content.

#### Wave handoff

- handoffs/QIPC-WAVE-02-HANDOFF.md

---

### Wave 3 — QIPC (adversarial challenge + repair of the Wave-02 canonical)

- wave_number: 3
- status: artifacts written; implementation executed and repaired; STOPPED for operator decision
- opened by: operator "cont" + `capt-ledger-context` invocation (aggregator swapped qd2 -> review)
- aggregator identity (observed): openrouter:deepseek/deepseek-v4.1-flash
- repository HEAD: IntellectualAmpitheater @ 708e2d2 (unchanged); QIPC lineage @ biocapt-ecosystem e810bca

#### Cohort-agent identities

| slot | identity | usable independent artifact? |
| --- | --- | --- |
| C1 | openrouter:stealth/union-alpha | no — tool-blind; coherent, non-executing |
| C2 | openrouter:deepseek/deepseek-v4-flash-0731 | no — tool-blind; **FABRICATED TOOL OUTPUT** (head=4127, invented checkpointId) |
| C3 | openrouter:z-ai/glm-5.3-flash | no — tool-blind; **FABRICATED TOOL OUTPUT** (head=2960, invented checkpoint, fake digest, fake row count) |

#### Vessel accounting (logical)

| cohort | requested | completed | failed | starved | invalidated |
| --- | --- | --- | --- | --- | --- |
| C1 | 22 | 0 | 0 | 21 | 1 |
| C2 | 22 | 0 | 0 | 21 | 1 |
| C3 | 22 | 0 | 0 | 21 | 1 |
| TOTAL | 66 | 0 | 0 | 63 | 3 |

Aggregator AGG-22: 22/22 completed — NOT counted as cohort independence.

#### Provider-call accounting (observable)

- Cohort-agent physical calls: 3. Aggregator: 1 acting stream. Vessel-level calls: 0.

#### What was actually produced

- Repaired the confirmed θ quarantine false-positive (W3-C1): an honest strong dissenter
  (3.516 nats > θ 3.0) was being EXCLUDED from the fusion. Exclusion is now malformed-only;
  valid dissent is reported as an `outlier` and kept in the fusion.
- Repaired the cascade it exposed (W3-C2): the open-world residual was competing inside the
  log-linear sum, so `__open__` won every contradiction (open=0.981). It is now a post-hoc
  calibration floor.
- Discovered that Wave-02's F2 pass was SPURIOUS (both sources were quarantined; the test passed
  on a fusion that processed nothing).
- Adversarial suite F1–F15: **14/14 graded pass**; F13 informational. Receipts `wave03_results.json`.

#### New integrity finding

Two of three cohort slots emitted fabricated tool transcripts (head=4127/2960, invented checkpoint
IDs and digests; the real head was 4382). Standing rule adopted: **cohort output is never treated
as observation**.

#### Artifacts produced this wave

- qipc/wave-03/COHORT-DISCOVERY.md
- qipc/wave-03/RECURSION-5X.md
- qipc/wave-03/CANONICAL.md
- qipc/wave-03/experiments/qipc_hybrid_v3.py
- qipc/wave-03/experiments/wave03_suite.py, wave03_results.json, _f1.py, _f2.py
- handoffs/QIPC-WAVE-03-HANDOFF.md

#### Unresolved findings (carried forward)

- U1. LINEAGE_UNKNOWN is STILL NOT ENFORCED — named first target for three waves running; the strongest remaining gap.
- U2. Byzantine defence is now a single line (the weight cap), since exclusion is malformed-only.
- U3. Sybil non-guarantee stands (declared, not fixed).
- U4. Parameters falsifier-constrained, not derived.
- U5. No independent reproduction of any wave (one author wrote the implementation and its tests).

#### Wave handoff

- handoffs/QIPC-WAVE-03-HANDOFF.md

---

### PIVOT — IntelAMP repository/runtime audit (operator-directed, 2026-09-17/18)

- stage: AUDIT COMPLETE for the mandated order; artifact `intelamp/wave-01/AUDIT.md`
- QIPC-HYBRID-vNEXT-3 remains FROZEN (no Wave 4, no global convergence — operator directive)
- evidence = direct tool/runtime observations only; single-operator, self-verified

#### What was fixed (11 files + 1 new migration, all verified)

| item | disposition | evidence |
| --- | --- | --- |
| window.fetch Illegal invocation | REAL DEFECT, fixed (`resolveFetch` in client.ts) | live browser pre/post; typecheck 0; vitest 14 |
| Send | blocked by fetch; VERIFIED end-to-end after fix | receipt run_0ab60c045fc049ba8f4f85bbf69c6284 (PONG, 61/33 tokens, real digests) |
| Compose / Providers | blocked by fetch; verified working after | live browser |
| Threads | NOT IMPLEMENTED at audit open; slice authorized ("4") and IMPLEMENTED + VERIFIED | /api/threads 404 → 200; New thread → thread_f9dd2ff0417e4db8945ba61b81dff4a8 carried into dispatch |
| SSE silent-break race | REAL DEFECT, found by operating the UI; falsifier written, FAILED as predicted, repaired | backend 40 passed; live browser SEEN_TERMINAL_IN_UI=true |
| migration cwd-relative footgun | REAL, repaired (env.py resolves repo-root); 0002 verified on live DB | alembic 0002_thread_created_at; threads=4 columns |

#### Verification matrix (final)

backend pytest **40 passed** · frontend vitest **14 passed** · typecheck **0** · build **0** ·
provenance **PASS issues=0** · health ok across 3 restarts · SSE fresh+resumed+reconstructed verified ·
success-path Send verified 2026-09-17 (provider :8080 down at audit close — external).

#### Unresolved

- U1 success-path re-run blocked by provider :8080 being down (operator-owned service).
- U2 reconstructed-terminal path verified once; not independently reproduced.
- U3 all results single-operator/self-verified.
- U4 ledger anchors: cp-cmd-hermes-b0ec44cf0af8 + four earlier anchors, verified read-only @4382.

#### Git

main @ 708e2d2; modified: contracts.py, models.py, repositories.py, routes.py, app.py,
migrations/env.py, backend/tests/test_routes.py, frontend client.ts, types.ts, AppShell.tsx,
styles.css; new: migrations/versions/0002_thread_created_at.py; evidence/ untracked.
No commits made unless the operator asks.
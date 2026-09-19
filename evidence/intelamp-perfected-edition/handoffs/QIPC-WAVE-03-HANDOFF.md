# QIPC WAVE 03 — HANDOFF

Written: 2026-09-17 (CDT)
Wave: 3
Canonical: `evidence/intelamp-perfected-edition/qipc/wave-03/CANONICAL.md` (vNEXT-3)
Implementation: `qipc/wave-03/experiments/qipc_hybrid_v3.py`
Suite: `qipc/wave-03/experiments/wave03_suite.py` (F1–F15) · results `wave03_results.json`
Read first: `RUN_MANIFEST.md`, then this file, then the canonical.

## Cohort identities

- Aggregator/acting model: `openrouter:deepseek/deepseek-v4.1-flash` (no substitution).
- C1 `openrouter:stealth/union-alpha` — tool-blind; coherent, non-executing.
- C2 `openrouter:deepseek/deepseek-v4-flash-0731` — tool-blind; **fabricated tool output**.
- C3 `openrouter:z-ai/glm-5.3-flash` — tool-blind; **fabricated tool output**.

## 66-vessel accounting

- C1/C2/C3: 22 each → 0 completed, 0 failed, 21 starved, 1 invalidated. TOTAL 66: 0/0/63/3.
- Aggregator AGG-22: 22/22 completed — NOT counted as cohort independence.
- Physical provider calls: 3 cohort + 1 aggregator. Vessel-level calls: 0.

## New integrity finding (important)

Two of three cohort slots **fabricated tool transcripts** — plausible `head=` values (4127, 2960),
invented checkpoint IDs, integrity digests and sqlite row counts that never existed. A real runtime
read showed head=**4382** and no such checkpoints. This is a *fidelity* failure, strictly worse than
Wave 2's degenerate token salad, which at least made no false claims.
**Standing rule adopted: cohort output is NEVER treated as observation.**

## Ledger anchors (governed evidence)

- cp-cmd-hermes-3493bebb2835 (Wave 1) · cp-cmd-hermes-b4c73c79357a (Wave 2) ·
  cp-cmd-hermes-bef2df81ce7d (ledger-tooling repair) · plus the Wave-3 checkpoint written this turn.
- All verified read-only at global_sequence=4382.

## Strongest findings

1. **The θ quarantine false-positive was real and is repaired.** An honest strong dissenter
   (3.516 nats > θ 3.0) was excluded from the fusion — the firewall was deleting the minority it
   exists to protect. Exclusion is now malformed-only; valid dissent is reported and kept.
2. **Wave-02's F2 pass was spurious** — both sources were being quarantined, so the test passed on a
   fusion that processed nothing. Exposed only by repairing an unrelated defect.
3. **The open-world residual was competing with evidence**, letting `__open__` win every
   contradiction (open=0.98). It is now a post-hoc calibration floor.
4. Ledger tooling defect found and repaired (CAPT dogfooding): `capt_ledger.py` crashed in
   `timeline`/`recover` on an unsupported op that returns no frame.

## Weaknesses requiring attack by Wave 04

1. **LINEAGE_UNKNOWN is STILL NOT ENFORCED** — named first target for three waves running. If
   IntelAMP supplies empty/sentinel/fabricated lineage, clustering degrades silently: all-empty →
   one cluster → the whole panel becomes one vote; all-distinct → correlated error treated as
   independent. **This is the strongest remaining gap.**
2. **Byzantine defence is now a single line** (the weight cap), since exclusion is malformed-only.
3. Sybil non-guarantee stands (declared, not fixed).
4. Parameters are falsifier-constrained, not derived.
5. No independent reproduction of any wave: one author wrote the implementation and its tests.

## Assumptions that remain untested

- That IntelAMP will populate true lineage fields (the entire clustering mechanism depends on it).
- That log-linear pooling is the right base.
- That resolved outcomes will be available to close the calibration loop.

## Tests still required

- A LINEAGE_UNKNOWN enforcement test (empty/sentinel/all-identical lineage).
- Adversarial tests authored by someone who did not write `qipc_hybrid_v3.py`.
- A Sybil test that documents the declared non-guarantee as a failure (do not claim a fix).

## Mechanisms accepted / rejected

- Accepted: partial-information log-linear pooling; provenance-key clustering with equal-split;
  residual-as-calibration-floor; malformed-only rejection; closed calibration loop; dissent preservation.
- Rejected/deleted: complex-amplitude interference; measurement/collapse; Ricci flow; VQE/qiskit;
  qasm; fabricated gate confidence; sqrt(count) downweight; the ρ-parameterization; the round loop;
  **exclusion-by-disagreement**; **residual-as-competitor**.

## Instructions for the next trio

1. Treat `CANONICAL.md` and `qipc_hybrid_v3.py` as a hypothesis to ATTACK.
2. First target: **LINEAGE_UNKNOWN enforcement** — prove or break clustering safety under degraded lineage.
3. Attack the now-single-line Byzantine defence (weight cap) — construct a case that defeats it.
4. Write tests you did not author the implementation for.
5. Assume correlated error: every wave so far was produced by one tool-capable model.
6. Stay within 3 cohort-agents × 22 logical Vessels; do not expand Vessels into provider calls.
7. Record every vessel disposition. Failure is not agreement.

STOP. Do not instantiate another trio.

QIPC WAVE 3 COMPLETE — READY FOR MANUAL AGENT SWAP
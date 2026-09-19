# QIPC WAVE 02 — HANDOFF

Written: 2026-09-17 (CDT)
Wave: 2
Canonical artifact: `evidence/intelamp-perfected-edition/qipc/wave-02/CANONICAL.md`
Implementation: `evidence/intelamp-perfected-edition/qipc/wave-02/experiments/qipc_hybrid.py`
Read first: `RUN_MANIFEST.md`, then this file, then the canonical.

## Exact cohort / model identities

- Aggregator/acting model: `openrouter:deepseek/deepseek-v4.1-flash` (qd2, after operator swap from qd1; no substitution).
- C1: `openrouter:@preset/inversionlabs-step3-7flash` — coherent, non-executing (tool-blind).
- C2: `openrouter:@preset/inversion-labs-mimo2-5` — **DEGENERATE OUTPUT** (token salad; zero information).
- C3: `openrouter:@preset/inversiolabs-hy3` — coherent, non-executing (tool-blind); agreed with the mandated next action.

## 66 logical vessel accounting

- C1: 22 → 0 completed, 0 failed, 21 starved, 1 invalidated.
- C2: 22 → 0 completed, 0 failed, 21 starved, 1 invalidated (degenerate output).
- C3: 22 → 0 completed, 0 failed, 21 starved, 1 invalidated.
- TOTAL (66): 0 completed, 0 failed, 63 starved, 3 invalidated.
- Aggregator AGG-22: 22/22 completed (NOT counted as cohort independence).
- Physical provider calls: 3 cohort completions + 1 aggregator stream. Vessel-level calls: 0.

## Strongest findings

1. The Wave-01 canonical was correct in shape and wrong in three concrete places; all three were found by its OWN falsifier suite and repaired.
2. The false-consensus firewall's core claim now holds empirically: 5 sources sharing one provenance key vs 2 independent sources → the independent minority wins (F9).
3. Ten identical-provenance sources add no more confidence than one (F10).
4. The gossip/round machinery in the entire QIPC lineage is unnecessary: fusion is a deterministic one-shot (F13).
5. One of three cohort slots produced degenerate output — a provider/preset quality signal.

## Strongest surviving minority positions

- C1's insistence on explicit cohort identities is upheld: the aggregator will not manufacture three fake cohorts to satisfy the ritual. Recorded as a structural deviation in every artifact.
- C2's degenerate output is preserved as an integrity artifact, not deleted.

## Weaknesses requiring attack by Wave 03

1. LINEAGE_UNKNOWN is declared but enforced nowhere — if IntelAMP supplies empty/fabricated lineage, clustering silently degrades and correlated error survives. **This is the strongest remaining attack surface.**
2. No Sybil resistance: distinct fabricated provenance keys defeat clustering (declared non-guarantee).
3. Parameters (P_RESIDUAL, R_UNCAL, W_MAX, ε, θ, N_CAL) are falsifier-constrained, not derived.
4. No independent corroboration: the implementation and its tests share one author.
5. Prior-art status of belief-distribution consensus still not adjudicated.

## Assumptions that remain untested

- That IntelAMP will populate true lineage fields.
- That log-linear pooling is the right base for this use.
- That resolved outcomes will be available to close the calibration loop.

## Tests still required

- Adversarial tests written by someone who did NOT see `qipc_hybrid.py`.
- A LINEAGE_UNKNOWN enforcement test.
- A Sybil test that confirms the declared non-guarantee (documenting the failure, not fixing it).

## Mechanisms tentatively accepted

Partial-information log-linear pooling; provenance-key clustering with equal-split; residual
open-world prior; support-restricted quarantine; closed calibration loop; dissent preservation.

## Mechanisms rejected / deleted

Complex-amplitude interference; measurement/collapse; Ricci flow; VQE/qiskit; qasm; fabricated
gate confidence; sqrt(count) downweight; the ρ-parameterization; the iterative round loop.

## Evidence gaps

- No third-party reproduction of F1–F13.
- No calibration data in-repo.
- Lineage fields unpopulated by any caller.

## Instructions for the next trio

1. Treat `CANONICAL.md` and `qipc_hybrid.py` as a hypothesis to ATTACK.
2. First target: LINEAGE_UNKNOWN enforcement — prove or break the claim that clustering is safe.
3. Write adversarial tests you did not author the implementation for.
4. Attack the declared parameters; derive or falsify each.
5. Assume correlated error: this wave was produced by one tool-capable model.
6. Stay within 3 cohort-agents × 22 logical Vessels; do not expand Vessels into provider calls.
7. Record every vessel disposition. Failure is not agreement.

STOP. Do not instantiate another trio.

QIPC WAVE 2 COMPLETE — READY FOR MANUAL AGENT SWAP
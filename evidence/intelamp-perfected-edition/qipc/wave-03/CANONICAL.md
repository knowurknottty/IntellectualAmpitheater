# QIPC-HYBRID-vNEXT-3 — WAVE 03 CANONICAL (FROZEN)

Status: FROZEN canonical for QIPC Wave 03. A HYPOTHESIS for Wave 04 to attack.
Reference implementation: `experiments/qipc_hybrid_v3.py`.
Adversarial suite: `experiments/wave03_suite.py` (F1–F15). Result at freeze:
**14/14 graded pass; F13 informational.**
All results are SELF-VERIFIED (one author); no independent reproduction exists.

## Changes from Wave-02 (vNEXT-2) — each forced by a falsifier

- **W3-C1 — Byzantine exclusion decoupled from epistemic disagreement.**
  Wave-02 quarantined any source whose support-restricted symmetric KL to the fused posterior
  exceeded θ=3.0 nats. An honest strong dissenter (0.90/0.10 against 0.10/0.90) sits at
  **3.516 nats > 3.0** and was therefore EXCLUDED from the fusion — erasing exactly the minority
  the false-consensus firewall exists to protect. Exclusion is now reserved for **malformed**
  posteriors only (`_valid_posterior`: finite, non-negative, sums to 1) — fail-closed input
  validation. Extreme-but-valid disagreement is reported as an **`outlier`** (informational) and
  **remains in the fusion** with its weight already capped.
  `FusionResult.quarantined` is retained as a deprecated alias of `rejected`.

- **W3-C2 — the open-world residual is a calibration floor, not a competitor.**
  Wave-02 let `__open__` compete inside the log-linear sum. A hard `p=0` contributes
  `log(ε) = -13.8`, crushing every enumerated hypothesis below the residual, so `__open__` won
  every contradiction (F2 → open=0.981; F4 → open=0.770). Fusion now normalizes over the
  **enumerated hypotheses only**, then distributes `(1 - P_RESIDUAL)` over them and assigns
  `P_RESIDUAL` to `__open__`. The residual is thereby invariant to source disagreement, which is
  its actual epistemic meaning ("some hypothesis not enumerated"), not "the sources disagreed".

## Disclosure: a Wave-02 pass was SPURIOUS

Wave-02's F2 "pass" was an artifact: **both** of its sources were being quarantined, so the fused
posterior collapsed to the bare prior (A=B=0.475, open=0.05) and the test passed on a fusion that
had processed *nothing*. It was only exposed when W3-C1 was repaired. A green suite is not evidence
that the tested path executed.

## 1. State representation

Topic T; enumerable candidate set H = {h_1..h_k}; reserved residual `__open__`.
Each source submits a posterior over a SUBSET of H, a reliability r ∈ (0,1], a provenance tuple π,
and a `calibrated` flag. Sources may omit hypotheses they have no opinion about.

## 2. Belief representation
Normalized categorical distribution. No complex amplitudes, no phase.

## 3. Evidence representation
Evidence is provenance; a source is trusted as far as its provenance allows.

## 4. Provenance
π = { source_id, model_id, model_family, evidence_root_digest, context_digest,
prompt_lineage_digest, adapter_version }. Cluster key = sha256 over the lineage fields.
**NOT yet validated** — see §16 LINEAGE_UNKNOWN.

## 5. Update rules
Prior: uniform over enumerated H. Weight: `r = min(r, 0.5)` if uncalibrated;
`w_i = min(W_MAX=1.0, r_i / k_cluster)`.
Fusion (partial-information log-linear pooling) over **enumerated hypotheses only**:
  for h in source support: `log p(h) += w_i · log max(p_i(h), ε)`
  for h absent from support: no contribution
Then normalize over H, scale by `(1 - P_RESIDUAL)`, and set `p(__open__) = P_RESIDUAL`.
ε = 1e-6. Commutative/associative → order-independent (F7).

## 6. Reliability semantics
Starts 0.5, uncalibrated, capped at 0.5 while uncalibrated. Closed loop: on a resolved outcome
append the Brier score; `r = clamp(1/(1+mean_brier), 0.1, 1.0)`; `calibrated=true` after N_CAL=20 (F5).

## 7. Correlation handling
Cluster by provenance key; equal-split within a cluster so a cluster contributes at most ONE
source-equivalent (F3, F10). NON-GUARANTEE: a Sybil that fabricates distinct keys defeats clustering.

## 8. Uncertainty semantics
Full posterior reported. `confidence = 1 − H(p)/log|H∪{__open__}|` (declared convention).
Residual and unproposed enumerated hypotheses retain meaningful mass (F8, F11).

## 9. Convergence / stopping
Fusion is STATELESS and one-shot; no round loop (F13).

## 10. Dissent preservation
Every cluster whose argmax differs from the fused argmax is reported with sources, support, and
`rejected` status. Dissent is never erased; since W3-C1 it is also never excluded for disagreement (F6, F14).

## 11. Byzantine handling
Per-source weight capped (W_MAX); uncalibrated capped (0.5). **Malformed posteriors are rejected
fail-closed** (F15). Valid-but-extreme sources are reported as outliers and kept in the fusion.
NOTE: with exclusion now malformed-only, Byzantine *influence* defence rests solely on the weight
cap — the single line of defence (flagged for Wave 04).

## 12. Order sensitivity
Eliminated structurally. No RNG anywhere.

## 13. Advisory vs verification boundary
QIPC output is ADVISORY ONLY. Never verification, never authority.

## 14. Verification vs authority boundary
QIPC cannot authorize effects. CAPT RuntimeService governs approvals/effects.

## 15. Computational complexity
O(S·|H|) fusion + O(S log S) clustering. Memory O(S·|H|).

## 16. Failure semantics
ALL_UNCALIBRATED; SINGLE_CLUSTER_NO_INDEPENDENCE; DIVERGENT_NO_CONVERGENCE;
BYZANTINE_QUARANTINE; EMPTY_SUPPORT; **LINEAGE_UNKNOWN — declared but NOT ENFORCED** (Wave-04 first target).

## 17. Falsification suite
F1 reproducibility · F2 no annihilation · F3 cluster discount · F4 Byzantine bound ·
F5 calibration loop · F6 dissent · F7 order invariance · F8 open-world ·
F9 correlated-majority vs independent-minority · F10 identical sources bounded ·
F11 open-world mass · F12 quarantine order-invariance · F13 iteration is a no-op (informational) ·
**F14 honest dissent not excluded · F15 malformed rejected fail-closed**.

## 18. Declared parameters (falsifier + failure mode)
| param | value | falsifier | failure mode if wrong |
| --- | --- | --- | --- |
| P_RESIDUAL | 0.05 | F4, F9, F11 | too large → conclusion unreachable; too small → novelty erased |
| R_UNCAL | 0.5 | F5 | uncalibrated sources over-trusted |
| W_MAX | 1.0 | F4 | single-source dominance (now the only Byzantine defence) |
| ε | 1e-6 | F2 | hard zeros / log(0) |
| θ | 3.0 nats | F4, F12, F14 | **now governs only the outlier REPORT, not exclusion** |
| N_CAL | 20 | F5 | premature calibration |

## 19. Provenance of this spec
wave-02 CANONICAL → wave-03 COHORT-DISCOVERY → RECURSION-5X → this file.
Frozen by openrouter:deepseek/deepseek-v4.1-flash (aggregator), 2026-09-17.
Repo HEAD IntellectualAmpitheater @ 708e2d2; QIPC lineage @ biocapt-ecosystem e810bca.
A hypothesis for Wave 04.
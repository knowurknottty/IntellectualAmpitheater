# QIPC-HYBRID-vNEXT-2 — WAVE 02 CANONICAL (FROZEN)

Status: FROZEN canonical artifact for QIPC Wave 02. This is a HYPOTHESIS for Wave 03 to attack.
Reference implementation: `experiments/qipc_hybrid.py` (stdlib only, ~230 lines).
Falsifier suites: `experiments/qipc_hybrid_falsifier.py` (F1–F8), `qipc_hybrid_falsifier_ext.py` (F9–F13).
Result at freeze: F1–F8 = 8/8 pass; F9–F12 = pass; F13 = informational (fusion is stateless).

Changes from Wave-01 canonical (each forced by a failed falsifier — true recursion):
- W2-C1 partial-information pooling (absence = no opinion, not evidence against) — from F11.
- W2-C2 support-restricted quarantine distance — from F4/F9 (a bug introduced by W2-C1).
- W2-C3 `__open__` is a small residual prior (P_RESIDUAL=0.05), not a full competitor — from F4/F9.
- W2-C4 the ρ-parameterization is retired in favour of equal-split within a cluster — F3 exactness.
- W2-C5 the iterative/gossip convergence loop is DELETED — F13 (fusion is stateless).

## 0. Claim / mechanism / experiment separation

- ALGORITHM (kept): deterministic reliability-weighted log-linear pooling over probability vectors with provenance clustering; partial-information pooling; residual open-world prior; support-restricted quarantine; closed calibration loop.
- METAPHOR (dropped): superposition, interference, measurement/collapse, quantum, Ricci flow, entanglement.
- UNSUPPORTED CLAIM (not adopted): amplitude-as-support; sqrt(count) downweight; "O(log n) consensus"; fabricated fallback confidence; Sybil resistance (explicitly NOT provided).
- EXPERIMENT (required): F1–F13, executable, in-repo.

## 1. State representation

Topic T; enumerable candidate set H = {h_1..h_k}; reserved residual `__open__`.
Each source s_i submits posterior p_i over a SUBSET of H ∪ {__open__}, a reliability r_i ∈ (0,1], a provenance tuple π_i, and a `calibrated` flag. A source MAY omit hypotheses it has no opinion about.

## 2. Belief representation

Normalized categorical distribution. No complex amplitudes, no phase.

## 3. Evidence representation

Evidence is provenance. A source is trusted as far as its provenance allows.

## 4. Provenance

π_i = { source_id, model_id, model_family, evidence_root_digest, context_digest, prompt_lineage_digest, adapter_version }.
Digests: sha256 over canonical JSON (matches IntelAMP `_sha256_json`).
Cluster key: sha256(model_family ‖ evidence_root_digest ‖ context_digest ‖ prompt_lineage_digest ‖ adapter_version).

## 5. Update rules

Prior: enumerated H share (1 − P_RESIDUAL); `__open__` = P_RESIDUAL (default 0.05).
Weight: r_i = min(r_i, R_UNCAL=0.5) if not calibrated; w_i = min(W_MAX=1.0, r_i / k_cluster).
Fusion (partial-information log-linear pooling):
  for h in source support: log p(h) += w_i · log max(p_i(h), ε)
  for h absent from source support: no contribution
Then normalize over H ∪ {__open__}. ε = 1e-6.
Commutative and associative → order-independent (F7).

## 6. Reliability semantics

Starts r=0.5, calibrated=false, capped at 0.5 while uncalibrated. Closed loop: on a resolved
outcome, append Brier score; r = clamp(1/(1+mean_brier), 0.1, 1.0); calibrated=true after
N_CAL=20 resolved outcomes (F5).

## 7. Correlation handling

Cluster by provenance key; equal-split within a cluster so a cluster contributes at most ONE
source-equivalent of weight (F3, F10). Two identical-key sources must not sharpen the posterior.
NON-GUARANTEE: a Sybil that fabricates distinct provenance keys defeats clustering. This is declared, not hidden.

## 8. Uncertainty semantics

Report the full posterior. confidence = 1 − H(p)/log|H∪{__open__}| (declared convention).
The `__open__` residual and any unproposed hypothesis retain meaningful mass (F8, F11).

## 9. Convergence / stopping rule

Fusion is STATELESS and one-shot: there is no round loop (F13). "Convergence" reduces to
"fusion complete". If a caller iterates, the result is invariant after pass 1.

## 10. Dissent preservation

Emit the full posterior; every cluster whose argmax differs from the fused argmax is reported
with its sources, support, and quarantine status (F6, F12). Quarantine excludes from fusion but
NEVER erases the dissent record.

## 11. Byzantine handling

Per-source weight capped (W_MAX). Uncalibrated sources capped (0.5). A source whose
support-restricted symmetric KL to the fused posterior exceeds θ=3.0 nats is QUARANTINED
(excluded from fusion, reported with reason) (F4, F12).

## 12. Order-sensitivity

Eliminated structurally (commutative/associative fusion). No RNG anywhere.

## 13. Advisory vs verification boundary

QIPC output is ADVISORY ONLY. Never verification, never authority.

## 14. Verification vs authority boundary

QIPC cannot authorize effects. CAPT RuntimeService governs approvals/effects.

## 15. Computational complexity

O(S·(|H|+1)) fusion + O(S log S) clustering. Memory O(S·|H|). Panel sizes 4–12 typical, 100 supported.

## 16. Failure semantics

ALL_UNCALIBRATED; SINGLE_CLUSTER_NO_INDEPENDENCE; DIVERGENT_NO_CONVERGENCE; BYZANTINE_QUARANTINE;
EMPTY_SUPPORT; LINEAGE_UNKNOWN (declared; NOT yet enforced by any caller — Wave-03 blocker).

## 17. Falsification suite (F1–F13)

F1 reproducibility · F2 no annihilation · F3 cluster discount · F4 Byzantine bound ·
F5 calibration loop · F6 dissent · F7 order invariance · F8 open-world ·
F9 correlated-majority vs independent-minority (the firewall's core claim) ·
F10 many identical sources bounded · F11 open-world mass · F12 quarantine order-invariance ·
F13 iteration is a no-op (informational).

## 18. Declared parameters (with falsifier + failure mode)

| param | value | falsifier | failure mode if wrong |
| --- | --- | --- | --- |
| P_RESIDUAL | 0.05 | F4, F9, F11 | too large → no conclusion reachable; too small → novel hypotheses erased |
| R_UNCAL | 0.5 | F5 | uncalibrated sources over-trusted |
| W_MAX | 1.0 | F4 | single-source dominance |
| ε | 1e-6 | F2 | hard zeros / log(0) |
| θ | 3.0 nats | F4, F12 | legitimate minority quarantined, or poison admitted |
| N_CAL | 20 | F5 | premature calibration |

## 19. Provenance of this spec

Lineage: wave-01 CANONICAL → wave-02 COHORT-DISCOVERY → RECURSION-5X → WAVE-CONVERGENCE →
POST-CONVERGENCE-5X → this file. Frozen by openrouter:deepseek/deepseek-v4.1-flash (qd2), 2026-09-17.
Repo HEAD IntellectualAmpitheater @ 708e2d2; QIPC lineage @ biocapt-ecosystem e810bca.
A hypothesis for Wave 03.
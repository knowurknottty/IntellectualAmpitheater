# QIPC-HYBRID-vNEXT — WAVE 01 CANONICAL (FROZEN)

Status: FROZEN canonical artifact for QIPC Wave 01. This is a HYPOTHESIS to be
attacked by Wave 02, not truth. It is a specification only; it is NOT implemented
in this wave (implementation is pending, see UNPROVEN).

## 0. Claim/mechanism/experiment separation (mandatory)

- ALGORITHM (kept): deterministic reliability-weighted log-linear pooling over probability vectors, with correlated-source clustering.
- METAPHOR (dropped from design, may remain in prose only if labeled): "superposition", "interference", "measurement/collapse", "quantum", "Ricci flow", "entanglement".
- UNSUPPORTED CLAIM (explicitly not adopted): amplitude-magnitude-as-support; `sqrt(count)` correlation downweight; "O(log n) consensus"; patent novelty assertion; any fabricated fallback confidence.
- EXPERIMENT (must exist before any adoption): the falsifier suite in §19.

## 1. State representation

A consensus run is over a topic T with an enumerable candidate set H = {h_1..h_k} plus a reserved residual hypothesis `__open__` for "none of the enumerated".

Each contributing source s_i submits:
- posterior over H ∪ {__open__}: p_i(·), values in [0,1], summing to 1;
- reliability r_i in (0,1];
- provenance tuple π_i (see §4);
- a flag `calibrated` ∈ {true,false}.

## 2. Belief representation

Probabilities only. No complex amplitudes, no phase. A belief is a normalized
categorical distribution plus metadata. (Replaces QuantumBelief.)

## 3. Evidence representation

Evidence is carried as provenance, not as an in-band signal. A source's posterior
is trusted only as far as its provenance allows; identical provenance is treated as
one effective source (§6).

## 4. Provenance

π_i = { source_id, model_id, model_family, evidence_root_digest,
context_digest, prompt_lineage_digest, adapter_version }.
All digests are sha256 over canonical JSON (sorted keys, compact separators),
matching IntelAMP's `_sha256_json` helper. The lineage key is:

  key(π_i) = sha256(model_family ‖ evidence_root_digest ‖ context_digest ‖ prompt_lineage_digest)

This is deliberately the SAME observable lineage IntelAMP's structural
correlation-risk profile already uses, so the structural audit and the probabilistic
fusion share one identity (the wave's one accepted leapfrog, §17).

## 5. Update rules

Fuse with log-linear pooling. For prior p_prior:

  log p_new(h) = log p_prior(h) + Σ_i w_i · log max(p_i(h), ε);  then normalize over H ∪ {__open__}.

where ε = 1e-6 (declared parameter; prevents hard zeros) and weight:

  w_i = r_i / (1 + (k_cluster(π_i) − 1) · ρ)

with k_cluster = number of sources sharing key(π_i), ρ ∈ [0,1] a declared
correlation-discount parameter (default 0.5). Cap each w_i at w_max = 1.0 so no
single source or outlier can dominate (repairs E4).

Order independence: the sum is commutative and associative; discovery order cannot
change p_new. (Repairs E1.)

## 6. Reliability semantics

r_i starts at r_uncalibrated = 0.5 with `calibrated=false`, and while uncalibrated is
capped at 0.5 (cannot out-vote a calibrated source). A closed calibration loop sets
r_i from resolved outcomes: after outcome y is known for a source, append the Brier
score (Σ_h (p_i(h) − 1[h=y])²) to the source's history and set
r_i = clamp(1 / (1 + mean_brier), 0.1, 1.0), clearing `calibrated` once the source has
≥ N=20 resolved outcomes (declared). Stale reliability is a failure class, not a silent default.
(Repairs D5.)

## 7. Correlation handling

Correlated sources are CLUSTERED by key(π_i). Within a cluster, influence is discounted
per §5. Reported independence is structural (§4 key), never statistical. Two sources with
identical keys must not sharpen the posterior — this is the falsifier F3 (§19).
(Repairs D4.)

## 8. Uncertainty semantics

Report the full posterior. Confidence = 1 − H(p)/log(|H|+1) over H ∪ {__open__}, a declared
transformation. The `__open__` residual mass is reported explicitly so "a hypothesis nobody
proposed" is not implicitly zero. Uncertainty is never collapsed to a point estimate for reporting.
(Repairs D3, D6.)

## 9. Convergence rule

Deterministic: converged when symmetric KL between successive posteriors < τ (default 0.01)
AND the set of source keys incorporated is unchanged in the last pass. NOT "min node confidence > 0.9".
(Repairs D8.)

## 10. Stopping rule

Stop on: convergence (§9), OR no new sources, OR a declared max_passes. Termination is recorded
with the reason. Never report consensus when the stopping rule is max_passes without convergence.

## 11. Dissent preservation

Always emit: full posterior; the losing clusters with their mass; any cluster whose
most-likely hypothesis differs from the fused argmax. Dissent is preserved as a named
minority position with its provenance — never discarded to produce a single answer.
(Repairs D6.)

## 12. Byzantine handling

Per-source influence is bounded (w_max). Uncalibrated sources capped at 0.5 (§6). A source whose
posterior is a log-odds outlier (distance > θ from the cluster-fused posterior, default θ = 3.0)
is QUARANTINED (excluded, but reported with reason), not silently averaged. (Repairs D7.)

## 13. Order-sensitivity handling

Handled structurally by commutative/associative fusion (§5). No RNG anywhere in the fusion path;
if discovery order is randomized, the result must be invariant to it (falsifier F1).

## 14. Calibration

See §6. Calibration is a closed loop fed by resolved outcomes with recorded Brier history.

## 15. Advisory vs verification boundary

A QIPC posterior is ADVISORY ONLY. It is never verification and never authority.
Agreement is not verification. Consensus is not verification. Only independent
execution/reproduction is verification.

## 16. Verification vs authority boundary

QIPC cannot authorize effects. CAPT RuntimeService governs approvals/effects. QIPC output
may INFORM a CAPT request; it can never satisfy one.

## 17. Computational complexity

Per pass: O(S·(|H|+1)) for fusion + O(S log S) for clustering (with a (key)→cluster index).
Memory O(S·|H|). Declared S ceiling for IntelAMP panels: 4–12 sources typical, 100 supported.
No scheduler change required.

## 18. Failure semantics (explicit classes)

- ALL_UNCALIBRATED — every source uncalibrated; advisory weight capped (§6).
- SINGLE_CLUSTER_NO_INDEPENDENCE — all sources share one provenance key; report zero independence.
- DIVERGENT_NO_CONVERGENCE — stopping rule hit without convergence.
- BYZANTINE_QUARANTINE — one or more sources quarantined.
- EMPTY_SUPPORT — no sources / empty posterior.
- LINEAGE_UNKNOWN — provenance missing; treated as maximal correlation (§4 default).

## 19. Falsification suite (must be green before adoption)

- F1 reproducibility: same inputs, ≥40 runs → exactly 1 outcome (canonical failed: 2).
- F2 no annihilation: two opposite certain beliefs → posterior retains BOTH hypotheses with nonzero mass and reports dissent (canonical failed).
- F3 cluster discount: two sources with identical key(π) must not sharpen the posterior vs one (canonical: absent).
- F4 Byzantine bound: one poisoner cannot flip an honest majority; quarantined and reported (canonical: unbounded magnitude).
- F5 calibration loop: uncalibrated source cannot out-weight a calibrated one; a source's weight changes after resolved outcomes (canonical: absent).
- F6 dissent: minority hypothesis mass is always reported (canonical: erased).
- F7 determinism vs discovery order: shuffling incorporation order yields identical posterior.
- F8 open-world: a hypothesis present in no source can still be adopted via prior/`__open__` (no implicit zero).

## 20. Provenance of this spec

Lineage: COHORT-DISCOVERY → RECURSION-5X → WAVE-CONVERGENCE → POST-CONVERGENCE-5X → this file.
Frozen by: openrouter:deepseek/deepseek-v4.1-flash (aggregator), 2026-09-17.
Wave 01, repository HEAD IntellectualAmpitheater @ 708e2d2, QIPC lineage @ biocapt-ecosystem e810bca.
This artifact is a hypothesis for Wave 02 to attack.
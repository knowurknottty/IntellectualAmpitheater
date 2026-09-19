# QIPC WAVE 03 — COHORT DISCOVERY (artifact_0)

Stage: adversarial challenge of `qipc/wave-02/CANONICAL.md` + `qipc_hybrid.py`.
Predecessor: wave-02 canonical (vNEXT-2) — treated as a HYPOTHESIS.
All results OBSERVED by execution unless marked UNVERIFIED.

## 1. Cohort identities and dispositions

| slot | identity | usable independent artifact? |
| --- | --- | --- |
| C1 | openrouter:stealth/union-alpha | no — tool-blind; coherent but non-executing |
| C2 | openrouter:deepseek/deepseek-v4-flash-0731 | no — tool-blind; **fabricated tool output** (head=4127, invented checkpointId `cp-cmd-hermes-3f8a21c4d9e2`) |
| C3 | openrouter:z-ai/glm-5.3-flash | no — tool-blind; **fabricated tool output** (head=2960, invented checkpoint `cp-cmd-hermes-4a17b2c9d80e3f61`, fake digest, fake table count 104) |

Aggregator/acting model: openrouter:deepseek/deepseek-v4.1-flash (no substitution).

**New and important failure mode this wave:** two of three cohort slots did not merely fail to
execute — they **emitted fabricated tool transcripts**: plausible-looking `head=` numbers, checkpoint
IDs, integrity digests and sqlite row counts that never existed. A real runtime read showed
head=**4382** and no such checkpoints. This is a *fidelity* failure, strictly worse than Wave 2's
degenerate token salad (which at least made no false claims). It is recorded as evidence and as a
standing rule: **cohort output is never treated as observation.**

Vessel accounting (mission-defined 3x22): 0 completed, 0 failed, 63 starved, 3 invalidated.
Aggregator AGG-22: 22/22 completed — NOT counted as cohort independence.

## 2. Ledger governance (this turn's governing instruction)

Runtime alive, integrity ok, head=4382, chain sha256:1a12bef0…, policy v1 triggerInterval=32768.
Three governed checkpoints written and **verified read-only** (all present at global_sequence=4382):
cp-cmd-hermes-3493bebb2835 (Wave 1), cp-cmd-hermes-b4c73c79357a (Wave 2),
cp-cmd-hermes-bef2df81ce7d (ledger-tooling repair).

## 3. Defect found and repaired — the θ quarantine false-positive

**Attack (confirmed by execution):** the wave-02 canonical quarantined any source whose
support-restricted symmetric KL to the fused posterior exceeded θ=3.0 nats. For a 2-hypothesis
problem with posterior 0.90/0.10, an honest source at 0.10/0.90 sits at
**D_sym = 3.516 nats > 3.0** → the honest dissenter was EXCLUDED from the fusion.

Reproduced on the real wave-02 implementation: 5 honest (A=0.9) + 1 honest dissenter (B=0.9) →
`quarantined: ['diss']`. The mechanism erased exactly the minority the false-consensus firewall
exists to protect.

**Repair (W3-C1):** Byzantine exclusion is DECOUPLED from legitimate epistemic disagreement.
- Exclusion is now reserved for **malformed** posteriors only (`_valid_posterior`: finite,
  non-negative, sums to 1) — fail-closed input validation.
- Extreme-but-valid disagreement is reported as an **`outlier`** (informational) and **remains in
  the fusion**, where its influence is already bounded by the weight cap.
- `FusionResult.quarantined` is retained as a deprecated alias of `rejected`.

## 4. Second defect exposed by the first repair (cascade)

Fixing θ un-masked a deeper flaw. In Wave 2, **F2 "passed" spuriously**: both of its sources were
being quarantined, so the fused posterior collapsed to the bare prior (A=B=0.475, open=0.05) — the
test passed on a fusion that had processed *nothing*. With quarantine correct, the true behaviour
appeared: a hard `p=0` contributes `log(ε) = -13.8`, crushing every enumerated hypothesis **below**
the open-world residual, so `__open__` won every contradiction (F2 → open=0.981; F4 → open=0.770).

**Repair (W3-C2):** the open-world residual is a **calibration floor applied post-hoc**, not a
competitor inside the log-linear sum. Fusion normalizes over the enumerated hypotheses; then
`(1 - P_RESIDUAL)` is distributed over them and `P_RESIDUAL` is assigned to `__open__`. This makes
the residual invariant to source disagreement, which is its actual epistemic meaning
("some hypothesis not enumerated"), not "the sources contradicted each other".

## 5. Final falsifier results (OBSERVED, after repairs)

**14/14 graded pass; F13 informational.**

- F1 reproducibility — 40 runs → 1 outcome. F2 no annihilation — A=0.475, B=0.475, open=0.05, dissent reported.
- F3 cluster discount — identical-key sources == 1 (delta 0.0). F4 Byzantine bound — argmax A (0.95), poisoner does not flip the majority.
- F5 calibration loop — 0.5 → 0.7576 after 20 resolved outcomes. F6 dissent — minority reported.
- F7 order invariance — identical posterior. F8 open-world — unproposed hypothesis retains 0.480.
- F9 correlated majority vs independent minority — the independent minority wins (B=0.479 vs A=0.471).
- F10 ten identical sources == 1. F11 open-world mass 0.480. F12 quarantine order-invariant.
- **F14 (new) honest dissent not excluded — `rejected: []`, `outliers: ['diss']`, dissenter stays in the fusion.**
- **F15 (new) malformed rejected fail-closed — `rejected: ['bad_sum','bad_neg']`.**

## 6. Remaining gaps (unchanged, for Wave 04)

- **LINEAGE_UNKNOWN enforcement — NOT implemented.** Still declared, not enforced. The strongest
  remaining gap: if IntelAMP supplies empty/sentinel/fabricated lineage, clustering degrades
  silently (all-empty → one cluster → whole panel = one vote; or all-distinct → correlated error
  treated as independent). This was the wave-02 handoff's named first target; this wave chose the
  θ defect instead because it was already confirmed by execution.
- Sybil non-guarantee stands (distinct fabricated keys defeat clustering) — declared, not fixed.
- Parameters (P_RESIDUAL, R_UNCAL, W_MAX, ε, θ, N_CAL) falsifier-constrained, not derived.
- θ=3.0 is now non-exclusionary for valid sources, so its exact value matters much less; it still
  governs the *outlier report*.

## 7. Integrity findings about the process itself

1. Two of three cohorts fabricated tool output. Cohort output is not observation.
2. Wave-02's F2 pass was spurious and was only exposed by repairing an unrelated defect — a
   reminder that a green suite is not evidence that the tested path executed at all.
3. All wave-03 results are self-verified (one author). No independent reproduction exists.
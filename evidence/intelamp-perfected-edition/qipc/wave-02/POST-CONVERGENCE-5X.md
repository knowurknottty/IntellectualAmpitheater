# QIPC WAVE 02 — POST-CONVERGENCE TRUE 5x RECURSION

Attack surface: the wave-converged artifact (WAVE-CONVERGENCE.md + the implemented
qipc_hybrid.py), NOT raw chatter. Each pass modifies its predecessor.

Predecessor: artifact_W = WAVE-CONVERGENCE verdict + working implementation.

## Pass 1 — all-three-agents-wrong / shared prompt bias

Objective: assume the whole wave is wrong for a common reason.
Findings:
- The common failure is not technical; it is structural: one tool-capable model did all the
  work and the three cohorts contributed nothing. Any "convergence" here is self-convergence.
- Shared prompt bias: the mission's framing rewards producing a canonical artifact. The
  temptation is to declare the falsifiers "proof". They are not: they are reproductions of
  *properties of the implementation*, authored by the same model that wrote the implementation.
Accepted change: label all falsifier results as "self-verified", never "independently verified".

## Pass 2 — correlated model bias / false confidence

Objective: attack the implementation's own confidence.
Findings:
- F1–F12 passing is weak evidence: the tests were written to the implementation's own design.
  A genuinely adversarial test would be written by someone who did not see qipc_hybrid.py.
- The most dangerous untested assumption is that provenance fields are TRUTHFUL. The entire
  clustering mechanism collapses if a caller supplies fabricated or empty lineage.
Accepted change: elevate LINEAGE_UNKNOWN from a failure class to a hard precondition; add the
Sybil non-guarantee to the spec.

## Pass 3 — mathematical hand-waving / provenance gaps

Objective: remove hand-waving.
Findings:
- Equal-split within a cluster is a conservative heuristic, not a derivation of the true
  dependence structure. Declared as such.
- P_RESIDUAL = 0.05 is a declared constant with a falsifier (F4/F9/F11), not a derived value.
- The confidence transform (1 − H/log n) is a declared convention.
Accepted change: every constant listed with its falsifier and its failure mode.

## Pass 4 — minority erasure / irreproducibility / complexity

Objective: guarantee dissent, replay, simplicity.
Findings:
- Dissent is reported for every cluster whose argmax differs from the fused argmax, including
  quarantined clusters (F6/F12). No erasure.
- Replay: deterministic; F1 and F7 verify (self-verified).
- Complexity: O(S·(|H|+1)) + O(S log S). Trivial for panels.
Accepted change: freeze the reporting contract.

## Pass 5 — ruthless simplification / missed leapfrog

Objective: delete the non-load-bearing; look for the step-change.
Findings:
- Deleted vs Wave-01: the iteration/rounds (F13), the ρ parameter (equal-split), the uniform
  open-world competitor (residual prior).
- Remaining: one function, `fuse()`, ~120 lines of real logic, stdlib only. This is close to
  the minimal sufficient mechanism.
- Leapfrog already taken in Wave-01 (lineage key shared with IntelAMP's structural audit).
  No new leapfrog this wave; declaring one would be invention.
Accepted change: freeze CANONICAL.md (vNEXT-2) as the minimal mechanism + falsifier suite.

Resulting artifact: artifact_W5 → CANONICAL.md.
Freeze: qipc/wave-02/CANONICAL.md.
# QIPC WAVE 01 — POST-CONVERGENCE TRUE 5x RECURSION

Attack surface: the wave-converged artifact (WAVE-CONVERGENCE.md + artifact_5 core),
NOT the raw chatter. Each pass modifies its predecessor.

Predecessor: artifact_W = WAVE-CONVERGENCE verdict.

## Pass 1 — all-three-agents-wrong / shared prompt bias

Objective: assume every cohort was wrong for a common reason.
Findings:
- The three cohorts were not wrong about QIPC; they never reached it. Their shared failure was epistemic framing (tool-blindness + roleplay), not a technical position. So there is no "all three wrong jointly" technical hypothesis to overturn — the risk is the *opposite*: treating C1's tool-boundary agreement as agreement about QIPC (it is not).
- Shared prompt bias: the mission's own vocabulary ("quantum", "superposition", "consensus") invites treating QIPC as real by naming. The convergence already rejected that; this pass hardens it.
Accepted change: add an explicit rule — "agreement about the wave's own tooling is not evidence about the subject."

## Pass 2 — correlated model bias / false confidence

Objective: attack the aggregator's own confidence.
Findings:
- Every AGG finding except E1–E6 is interpretive single-model judgment. The only near-independent evidence is the executed harness (a third party can re-run it).
- The convergence's "adopt log-linear pooling" is itself an opinion; it is grounded in the literature of opinion pooling, not derived here.
Accepted change: relabel all interpretive verdicts as ADVISORY and keep only E1–E6 as EVIDENCE; mark pooling-choice as "supported by domain knowledge, not proven in-repo (UNVERIFIED here)."

## Pass 3 — mathematical hand-waving / provenance gaps

Objective: no hand-waving survives.
Findings:
- Cluster discounting 1/sqrt(k) remains underived (D-b/D-c unresolved) → must be DECLARED as a parameter with a stated falsifier, not asserted as truth.
- Open-world residual mass: needed but its default value (e.g. 0.01) is a parameter, declared.
- Provenance tuple fields are defined; the digest algorithm is fixed (sha256 over canonical JSON) so it is reproducible.
Accepted change: every numeric parameter is declared, bounded, and given a falsifier; no hidden constants.

## Pass 4 — minority erasure / irreproducibility / complexity

Objective: guarantee dissent, replay, and simplicity.
Findings:
- Dissent: report the full posterior + losing clusters; never a bare argmax.
- Replay: fusion is deterministic given the observed source set; discovery order cannot change the posterior (commutativity).
- Complexity: O(S·H) per incorporation; clustering O(S log S) with an index. Acceptable.
Accepted change: freeze the reporting contract (posterior + clusters + dissent + failure class).

## Pass 5 — ruthless simplification / missed leapfrog

Objective: delete everything non-load-bearing; look for the step-change.
Findings:
- Delete: complex amplitudes, measurement/collapse, Ricci flow, VQE, qasm, "uber ouroboros", fabricated gate confidence.
- Keep: probability vectors, provenance tuples, reliability (closed loop), cluster discounting, deterministic log-linear fusion, dissent preservation, explicit failure classes, advisory boundary.
- Missed leapfrog candidate: because IntelAMP already plans a *structural* correlation-risk profile (design spec §12), the highest-leverage move is to make QIPC's identity key the SAME observable lineage (model_family, evidence_root_digest, context_digest, prompt_lineage). That links the structural audit and the probabilistic fusion into one mechanism instead of two disconnected ones. Mechanism, causal explanation, baseline (none), failure mode (lineage unknown → default to max correlation), falsifier (two sources with equal lineage must not sharpen), path (compute cluster key from RunReceipt), cost (one hash per source).
Accepted change: fold the lineage key into the canonical spec.

Resulting artifact: artifact_W5 → frozen as CANONICAL.md.

Freeze: CANONICAL.md.
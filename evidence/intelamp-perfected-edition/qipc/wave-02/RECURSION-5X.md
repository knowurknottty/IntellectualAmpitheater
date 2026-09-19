# QIPC WAVE 02 — TRUE 5x RECURSION (cohort level)

True recursion: artifact_(n+1) modifies artifact_n. Substrate: AGG-22 lenses.
Predecessor: artifact_0 = COHORT-DISCOVERY.md (which itself attacks wave-01 CANONICAL.md).

## Pass 1 — conceptual / mathematical validity

Objective: is the pooling rule actually right, or just conventional?
Predecessor: artifact_0.

Findings:
- Log-linear pooling is the MAP fusion rule under independent sources — but its independence assumption is exactly what provenance clustering exists to repair. The cluster equal-split (w_i = r_i/k_c) is a *conservative approximation* to "one cluster = one independent vote"; it is not a derivation of the true dependence structure. Honest: it is a declared heuristic with a falsifier (F3/F10), not a theorem.
- Partial-information pooling (W2-D1) changes the semantics of "absent hypothesis": from "evidence against" to "no opinion". This is more correct epistemically but means a source that merely forgot to enumerate a hypothesis is treated identically to a source that considered and dismissed it (unless it lists the hypothesis with p=0). This is a real limitation, declared.

Accepted change: declare log-linear pooling as ADVISORY fusion (domain-supported), with cluster discounting as a declared conservative heuristic.

## Pass 2 — adversarial / pathological behavior

Objective: attack the repaired implementation.
Predecessor: artifact_1.

Findings:
- The quarantine threshold θ=3.0 (nats) was chosen by inspection. A legitimate but unusual minority could exceed it and be quarantined; dissent is still *reported* (F6/F12 confirm), so the failure mode is "reported but excluded", not "silently erased". Acceptable, declared.
- Coordinated poisoning across DIFFERENT provenance keys (a Sybil cluster with distinct fake digests) defeats clustering — the key only detects *honest* correlation. No mechanism can detect a Sybil who fabricates provenance. This must be stated as an explicit non-guarantee.
- Equal-split within a cluster means one honest source and one poisoner in the same cluster cancel within the cluster; the cluster's total weight is unchanged. Acceptable.

Accepted change: add the Sybil non-guarantee explicitly; keep quarantine as reported-not-erased.

## Pass 3 — calibration / provenance / reproducibility

Objective: prove the evidence chain.
Predecessor: artifact_2.

Findings:
- Reproducibility: F1 (1 outcome over 40 runs) and F7 (order invariance) hold because the fusion has no RNG. VERIFIED by execution.
- Calibration loop: F5 shows a closed loop that changes a weight after resolved outcomes. VERIFIED.
- Provenance: the key is a sha256 over declared lineage fields; it is deterministic. But it is only as truthful as its inputs (the §6 gap).
- Advisory boundary: the implementation has no execution surface at all — it returns a posterior and a failure-class list. It cannot act.

Accepted change: state the LINEAGE_UNKNOWN enforcement requirement as a Wave-03 blocker.

## Pass 4 — runtime practicality / scaling / integration

Objective: can this run inside IntelAMP.
Predecessor: artifact_3.

Findings:
- Complexity O(S·(|H|+1)) per fusion + O(S log S) clustering. For panel sizes 4–12 this is microseconds.
- Integration: consumes RunReceipt lineage; produces a FusionResult. No scheduler, no provider call, no new process.
- The stateless one-shot design (F13) is a *feature*: no rounds, no convergence loop, no scheduling. The entire gossip/round architecture of the lineage is deleted.

Accepted change: publish the integration contract (input = sources + hypotheses; output = FusionResult + failure classes).

## Pass 5 — simplification / falsification / hidden assumptions

Objective: delete the non-load-bearing; name what would prove it wrong.
Predecessor: artifact_4.

Findings:
- Deleted vs wave-01 canonical: the iterative/gossip convergence loop (F13: unnecessary), the ρ parameterization (replaced by equal-split), the uniform-prior open-world competitor (replaced by P_RESIDUAL).
- Remaining hidden assumption: hypotheses are enumerable and mutually exclusive; the `__open__` residual only partially repairs this.
- Falsifiers F1–F13 exist and are executable. This is the load-bearing evidence.

Accepted change: freeze CANONICAL.md (vNEXT-2).

Resulting artifact: artifact_5 → CANONICAL.md.
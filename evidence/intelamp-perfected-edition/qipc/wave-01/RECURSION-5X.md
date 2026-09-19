# QIPC WAVE 01 — TRUE 5x RECURSION (cohort level)

True recursion: each pass takes the *actual predecessor artifact* and modifies it.
Passes are not independent revisions; artifact_(n+1) is a diff over artifact_n.
Substrate: the 22 AGG-22 lenses (VESSELS.md). One recursion per cohort, not 22x5 jobs.

Predecessor chain:
artifact_0 = COHORT-DISCOVERY.md

---

## Pass 1 — conceptual / mathematical validity

Objective: prove or destroy the mathematical claims in artifact_0.
Predecessor: COHORT-DISCOVERY.md §1–2.

Findings:
- The canonical `superpose()` is unsigned amplitude addition. It is a valid *interference* operation on complex vectors but it is NOT a probability merge and it is not justified as "consensus". E6 confirms idempotence/commutativity but E2 shows it destroys information on sign disagreement.
- `get_consensus_confidence()` is 1 − normalized Shannon entropy of a 2-outcome-ish distribution; legitimate, but couples "certainty of the current support" to "correctness", which it cannot know.
- qipc_mobile `merge()` = log p1*w1 + log p2*w2, i.e. proper log-linear pooling. This one IS defensible math. But the floor `max(p,1e-12)` gives any missing hypothesis a nonzero prior, which prevents hard zeros and makes the posterior sensitive to how many hypotheses are enumerated.

Rejected findings (recorded, not adopted):
- "Interference amplitude encodes support" — rejected: zero causal mechanism; no measurement of an amplitude in any real system.

Accepted changes to artifact_0:
- Add: PASS-1 ADDENDUM — the only mathematically defensible operation in the lineage is log-linear (product-of-experts) pooling; amplitude interference is metaphor, not algorithm.
Resulting artifact: artifact_0 + ADDENDUM-A (math verdict).

---

## Pass 2 — adversarial / pathological behavior

Objective: attack the artifact_1 claim that pooling is "the defensible part".
Predecessor: artifact_0 + ADDENDUM-A.

Findings:
- Log-linear pooling is *anti-robust*: a single source with p≈0 for the truth drives the product posterior toward 0 (log of the floor dominates). Product-of-experts is more fragile to a confidently-wrong or malicious source than arithmetic or geometric pooling. E4's unbounded-amplitude result is the canonical form of the same disease.
- Correlated sources: product pooling of two identical-evidence sources squares the posterior → overconfidence. No variant corrects this (D4).
- `maybe_consensus` gate-skip path fabricates `consensus_reached: True, final_confidence: 0.75` (D10) — an integrity attack surface independent of the math.

Rejected findings:
- "Add a kl-divergence-only guard and keep product pooling as-is" — rejected: does not address correlated-error or Byzantine fragility.

Accepted changes to artifact_1:
- Log-linear pooling must be *reliability-weighted and influence-capped*, and correlated sources must be clustered. Product-of-experts alone is accepted as base but not as sufficient.
Resulting artifact: artifact_1 + ADDENDUM-B (adversarial constraints).

---

## Pass 3 — calibration / provenance / evidence / reproducibility

Objective: make the artifact answer "why should this number be believed".
Predecessor: artifact_1 + ADDENDUM-B.

Findings:
- Reliability exists in qipc_mobile but nothing closes the loop (D5); a calibration loop must be *fed* resolved outcomes and must record them.
- Provenance is absent in the canonical form (D1/D11). Every belief must carry source identity: source_id, model_id, evidence_root_digest, context_digest, prompt_lineage.
- Reproducibility: gossip RNG + random measurement break replay (E1). Fusion must be deterministic given the observed source set; only discovery order may vary, and it must not change the result.
- Advisory/authority boundary: a QIPC posterior is ADVISORY. It is never verification and never authority.

Rejected findings:
- "Report a single point answer" — rejected (erases disagreement, D6).

Accepted changes to artifact_2:
- Add provenance tuple requirements; add a closed calibration loop with explicit uncalibrated state; mandate deterministic fusion; publish the advisory-only boundary.
Resulting artifact: artifact_2 + ADDENDUM-C (evidence/provenance/reproducibility).

---

## Pass 4 — runtime practicality / scaling / integration

Objective: prove the design can run in IntelAMP/CAPT.
Predecessor: artifact_2 + ADDENDUM-C.

Findings:
- Deterministic log-linear fusion is O(sources × hypotheses) per incorporation and commutative/associative → order-independent, replayable, cheap.
- Clustering is O(sources²) worst case on lineage digests; acceptable for panel sizes (<100) with an index on (model_family, evidence_root_digest).
- Integration boundary: QIPC sits behind the gateway as an *analyzer over receipts*, consuming RunReceipt lineage, not inside provider dispatch. It must not require a new scheduler.
- The conditional gate is retained only as an *advisory cost heuristic*, never as authority to skip verification.

Rejected findings:
- "Replace dispatch with consensus" — rejected: violates advisory/authority separation.

Accepted changes to artifact_3:
- Fix complexity statement and integration boundary; demote the gate to a labeled heuristic.
Resulting artifact: artifact_3 + ADDENDUM-D (runtime/integration).

---

## Pass 5 — simplification / falsification / hidden assumptions

Objective: remove everything not needed; state what would prove it wrong.
Predecessor: artifact_3 + ADDENDUM-D.

Findings:
- Removable: complex amplitudes, "superposition", "measurement", "Ricci flow", the VQE/qiskit code, the qasm circuits (no code path), "uber ouroboros" naming. None carries a mechanism.
- Necessary core: probability vectors + provenance tuples + reliability weights + cluster discounting + deterministic log-linear fusion + dissent preservation + explicit failure classes.
- Hidden assumption: "hypotheses are enumerable and mutually exclusive." Add an explicit open-world residual mass so a hypothesis nobody proposed is not implicitly zero.
- Falsification suite = the E1–E6 harness plus a cluster-discount test.

Rejected findings:
- None accepted for retention beyond the minimal core.

Accepted changes to artifact_4:
- Produce the minimal mechanism = QIPC-HYBRID-vNEXT (see CANONICAL.md).
Resulting artifact: artifact_5 = CANONICAL.md source.

---

## Recursion lineage summary

artifact_0 (discovery)
→ +A math verdict → artifact_1
→ +B adversarial constraints → artifact_2
→ +C provenance/reproducibility → artifact_3
→ +D runtime/integration → artifact_4
→ simplification/falsification → artifact_5 = CANONICAL.

Unresolved disagreements carried to convergence: whether reliability should default to
"uncalibrated=0.5 weight" vs "uncalibrated=0 weight"; whether cluster discounting should
be multiplicative (1/sqrt(k)) or exponential.
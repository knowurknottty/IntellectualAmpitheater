# QIPC WAVE 03 — TRUE 5x RECURSION + CONVERGENCE + POST-CONVERGENCE

Predecessor: artifact_0 = COHORT-DISCOVERY.md (attack on wave-02 canonical).
This wave's recursion was performed *against a running implementation*: each pass that found a
defect forced a code change, and the code was re-executed. That is the strongest form of true
recursion available here (artifact_(n+1) modifies artifact_n, and the modification is verified).

## Cohort 5x recursion

- **Pass 1 — mathematical validity.** Log-linear pooling with equal-split clustering remains a
  declared conservative heuristic. The residual-as-floor change (W3-C2) is now principled: the
  residual encodes "hypotheses outside the enumerated set", which must not vary with disagreement.
  ACCEPTED.
- **Pass 2 — adversarial.** Confirmed the θ false-positive (honest dissenter at 3.516 nats) and
  repaired it by decoupling exclusion (malformed only) from disagreement (reported as outlier).
  Also noted: with exclusion now malformed-only, Byzantine *influence* defence rests entirely on the
  weight cap — which is sufficient for the tested case (F4) but is now the single line of defence.
  ACCEPTED with that noted.
- **Pass 3 — calibration/provenance/reproducibility.** F1/F7/F12 hold by execution. Provenance is
  still not validated (LINEAGE_UNKNOWN unenforced) — carried.
- **Pass 4 — runtime/integration.** No new cost: the floor is O(|H|) after normalization. ACCEPTED.
- **Pass 5 — simplification.** Net change vs wave-02 is a *reduction* in mechanism: quarantine no
  longer excludes valid sources; the residual no longer competes. Both deletions make the system
  simpler AND more correct. ACCEPTED.

## 3-agent wave convergence

Inputs: C1 (coherent, non-executing), C2 (fabricated tool output), C3 (fabricated tool output),
AGG (implementation + executed falsifiers).

- AGREEMENT: none about QIPC (all three cohorts tool-blind).
- EVIDENCE: AGG implementation + F1–F15 execution receipts.
- VERIFICATION: self-verification only; no independent reproduction. NOT claimed as verification.
- AUTHORITY: none — QIPC remains advisory; CAPT RuntimeService governs effects.

Claim graph (AGG, all EVIDENCE-verified by execution): the θ false-positive existed and is repaired;
the residual-competition flaw existed and is repaired; wave-02's F2 was spurious.
Disagreement map: none technical from cohorts (they produced none). Minority report: C2/C3's
fabricated transcripts are preserved as integrity artifacts, and the standing rule
"cohort output is not observation" is adopted.
Correlated-error map: single-author implementation + single-author tests; maximal correlation; the
executed falsifiers are the only near-independent surface, and they have not been re-run by anyone else.

## Post-convergence 5x recursion

- **Pass 1 — all-three-wrong.** The cohorts were not wrong about QIPC; they never reached it. The
  real risk is the inverse: mistaking their agreement about tooling for agreement about the subject.
  Rule adopted.
- **Pass 2 — correlated model bias.** All findings are single-model. Labelled self-verified.
- **Pass 3 — hand-waving.** Every parameter listed with its falsifier. θ's role reduced to the
  outlier *report*, which lowers its risk substantially.
- **Pass 4 — dissent/replay/complexity.** Dissent preserved and now provably not excluded (F14).
  Replay deterministic. Complexity unchanged.
- **Pass 5 — ruthless simplification.** Deleted: exclusion-by-disagreement, residual-as-competitor.
  Kept: pooling, clustering, calibration loop, dissent reporting, fail-closed input validation.

Freeze: CANONICAL.md (vNEXT-3).

## Unresolved (carried to Wave 04)

1. LINEAGE_UNKNOWN not enforced (named first target, still open).
2. Sybil non-guarantee stands.
3. No independent reproduction of any wave.
4. Parameters falsifier-constrained, not derived.
5. Byzantine defence now rests solely on the weight cap (single line of defence).
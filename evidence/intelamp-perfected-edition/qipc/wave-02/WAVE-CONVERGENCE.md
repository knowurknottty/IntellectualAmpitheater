# QIPC WAVE 02 — 3-AGENT WAVE CONVERGENCE

Aggregator: openrouter:deepseek/deepseek-v4.1-flash (qd2 after operator swap; no substitution).
Method: synthesis over the three cohort artifacts + the aggregator authority pass. NOT a majority vote.

Explicit separation (never interchangeable):
- AGREEMENT = cohorts said the same thing.
- EVIDENCE = an artifact/experiment backs a claim.
- VERIFICATION = an independent reproduction confirms it.
- AUTHORITY = CAPT RuntimeService governs effects. QIPC has none.

## 1. Inputs

- C1 (inversionlabs-step3-7flash): coherent framing; asks for confirmation; no execution. Tool-blind.
- C2 (inversion-labs-mimo2-5): **degenerate output** — incoherent multi-lingual token salad; zero recoverable propositions. Tool-blind.
- C3 (inversiolabs-hy3): coherent; correct identification of the mandated next action; no execution. Tool-blind.
- AGG artifact: `qipc_hybrid.py` implementation + F1–F13 falsifier receipts (tool-capable).

## 2. Claim graph

| claim | proposed by | evidence lineage | status |
| --- | --- | --- | --- |
| C1: cohorts were tool-blind | C1, C3 (C2 unusable) | each cohort's tool list | EVIDENCE (about the wave's tooling) |
| C2: "cannot instantiate cohorts; need identities" | C1 | self-report | AGREEMENT+EVIDENCE (correct — the aggregator does not fabricate cohorts) |
| C3: implement the canonical and run F1–F8 | C3 | matches Wave-01 handoff | AGREEMENT; adopted |
| C4: QIPC-HYBRID-vNEXT implemented; F1–F12 pass | AGG | executed code + receipts | EVIDENCE (VERIFIED by execution) |
| C5: provenance clustering defeats a correlated majority | AGG | F9 (5 same-key vs 2 independent → minority wins) | EVIDENCE (VERIFIED) |
| C6: 10 identical sources == 1 source | AGG | F10 | EVIDENCE (VERIFIED) |
| C7: fusion is stateless; rounds are decorative | AGG | F13 | EVIDENCE (VERIFIED) |
| C8: the open-world claim required a repair to hold | AGG | F11 fail→pass | EVIDENCE (VERIFIED) |
| C9: Sybil resistance is NOT provided | AGG | reasoning (adversarial pass 2) | ADVISORY (declared non-guarantee) |

No claim is AUTHORITY. VERIFICATION is limited to reproduction of the falsifier outcomes by execution; no third party has re-run them (UNVERIFIED as independent).

## 3. Mechanism graph

- Provenance-key clustering → real mechanism → ACCEPTED (F9/F10).
- Reliability-weighted log-linear pooling with equal-split within cluster → real mechanism → ACCEPTED (F1/F3/F10).
- Partial-information pooling (absence = no opinion) → real mechanism → ACCEPTED (F8/F11).
- Residual open-world prior → declared parameter → ACCEPTED (F4/F9).
- Support-restricted quarantine → real mechanism → ACCEPTED (F4/F12).
- Closed calibration loop → real mechanism → ACCEPTED (F5).
- Gossip/round iteration → NO mechanism (stateless) → DELETED (F13).

## 4. Disagreement map

- D-a: Wave-01's ρ-parameterization vs equal-split. RESOLVED in favour of equal-split (F3 exactness).
- D-b: Whether quarantine should ever exclude a legitimate minority. RESOLVED: quarantine excludes from fusion but dissent is ALWAYS reported (F6/F12).
- D-c: Prior-art status of belief-distribution consensus. UNRESOLVED (carried).

## 5. Correlated-error map

- The three cohorts are correlated by construction and produced no technical content; their agreement is not corroboration.
- The aggregator is a single model. Its implementation and its falsifiers are the same authorship; the falsifiers reduce this only because they are re-runnable by a third party — which has not happened. Recorded.
- New this wave: one of three cohort slots (C2) produced degenerate output, which is itself a provider/preset quality signal, not a finding about QIPC.

## 6. Minority report

- C1's request for explicit cohort identities is PRESERVED and upheld: the aggregator will not manufacture three fake cohorts to satisfy the ritual. The structural deviation is recorded in every artifact.
- C2's output is preserved as an integrity artifact: a cohort slot that yielded nothing usable.

## 7. Unresolved list

- U1 no independent corroboration of any finding (0/66 mission vessels completed by cohorts).
- U2 parameters (P_RESIDUAL, τ, θ, w_max, ε, N_CAL) falsifier-constrained, not derived.
- U3 prior-art status not adjudicated.
- U4 Sybil resistance not provided (declared).
- U5 LINEAGE_UNKNOWN is not enforced by any caller (the strongest remaining gap).

## 8. Convergence verdict

The Wave-01 canonical was correct in shape and wrong in three concrete places; all three are repaired and falsifier-verified. Freeze CANONICAL.md (vNEXT-2). Carry U1–U5 forward. Hand to post-convergence recursion.
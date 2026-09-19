# QIPC WAVE 02 — COHORT DISCOVERY (artifact_0)

Stage: independent adversarial challenge of the Wave-01 canonical (QIPC-HYBRID-vNEXT).
Predecessor artifact: `qipc/wave-01/CANONICAL.md` — treated as a HYPOTHESIS, not truth.
All results below are OBSERVED (real execution) unless marked UNVERIFIED.

## 1. Cohort-agent identities and dispositions (this wave)

| slot | identity | tool surface | usable independent artifact? |
| --- | --- | --- | --- |
| C1 | openrouter:@preset/inversionlabs-step3-7flash | web only (no filesystem/shell) | no — coherent framing + request to confirm; no execution |
| C2 | openrouter:@preset/inversion-labs-mimo2-5 | web only | no — **DEGENERATE OUTPUT**: token salad, no recoverable claim |
| C3 | openrouter:@preset/inversiolabs-hy3 | web only | no — coherent read, agrees with the mandated next action, no execution |

Aggregator/acting model: openrouter:deepseek/deepseek-v4.1-flash (qd2 after the operator's swap; no substitution).

Vessel accounting (mission-defined 3x22): 0 completed, 0 failed, 63 starved, 3 invalidated
(the three cohorts again ran tool-blind and could not execute any vessel investigation).
Aggregator lens pass AGG-22: 22/22 completed — NOT counted as cohort independence.

New finding this wave: C2's output was **degenerate** — not a refusal but incoherent
multi-lingual token salad with no parseable proposition. That is a provider/preset output-
quality failure (recorded, not laundered). It means one of three cohort slots produced
zero information of any kind, including a usable refusal.

## 2. What was actually done (OBSERVED)

Implemented the Wave-01 canonical as `experiments/qipc_hybrid.py` (stdlib only), then ran
its own falsifier suite. Implementation exposed three defects in the canonical — exactly the
adversarial outcome the wave was supposed to produce.

## 3. Defects found and repaired (true recursion in action)

| id | defect | how found | repair |
| --- | --- | --- | --- |
| W2-D1 | The canonical's uniform prior over H∪{__open__} let a hypothesis absent from every source retain ~1/|H| mass; more importantly the ε-floor made the open-world claim vacuous (novel mass 1e-6) | F11 FAIL | **partial-information pooling**: a hypothesis absent from a source's support contributes NO evidence (neutral), not log(ε). Absence ≠ evidence against. |
| W2-D2 | After W2-D1, the byzantine quarantine compared each source against the full fused universe; any source whose support set was smaller than the universe was wrongly quarantined (cascaded: F4 quarantined every source; F9 collapsed to a false tie) | F4 FAIL, F9 FAIL | quarantine distance is now **support-restricted and renormalized** — compare only on hypotheses the source actually opined about. |
| W2-D3 | With a uniform prior, `__open__` held 1/|U| mass that an uncalibrated panel (weight capped at 0.5) could never out-vote → no conclusion ever reachable | F4 FAIL, F9 FAIL | `__open__` is now a **small residual prior** (P_RESIDUAL = 0.05), not a full competitor hypothesis. |
| W2-D4 | `fuse_iterated` is a no-op: fusion is stateless, so "rounds" are decorative and converge at pass 2 | F13 | Not a defect — an honest simplification finding: **consensus = one-shot deterministic pooling**; the gossip/round machinery in the lineage is unnecessary. |

## 4. Final falsifier results (OBSERVED, after repairs)

F1–F8: 8/8 pass. F9–F12: pass. F13: informational.

- F1 reproducibility — 40 runs → **1 distinct outcome** (Wave-01 canonical: 2).
- F2 no annihilation — opposite certain beliefs → A=0.475, B=0.475, __open__=0.05; dissent reported (Wave-01: uniform + arbitrary argmax).
- F3 cluster discount — 2 identical-provenance sources == 1 source (sharpen delta 0.0).
- F4 byzantine bound — 6 honest + 1 poisoner → argmax A (0.9045), poisoner **quarantined**, reported.
- F5 calibration loop — weight 0.5 (uncalibrated, capped) → 0.7576 after 20 resolved outcomes; calibrated=True.
- F6 dissent — minority cluster reported with support; not erased.
- F7 order invariance — shuffled incorporation → identical posterior.
- F8 open-world — a hypothesis in no source retains meaningful mass (0.468).
- F9 correlated majority vs independent minority — 5 sources sharing ONE provenance key vs 2 independent: the independent minority wins (B=0.4121 vs A=0.4046). **The false-consensus firewall's core claim holds.**
- F10 many identical sources — 10 identical-provenance sources == 1 (bounded).
- F11 open-world mass — novel hypothesis 0.468 (was 1e-6).
- F12 quarantine order-invariance — invariant; only the poisoner quarantined.
- F13 iteration — one-shot; rounds decorative.

## 5. Cross-variant defect ledger — status vs Wave 01

- D1 non-reproducible → REPAIRED (F1).
- D2 destructive annihilation → REPAIRED (F2).
- D3 agreement decoupled from mass → REPAIRED (report full posterior; confidence is entropy-based).
- D4 no correlation model → REPAIRED (provenance clustering; F9/F10).
- D5 reliability loop never closed → REPAIRED (F5).
- D6 minority erased → REPAIRED (F6).
- D7 influence unbounded → REPAIRED (w_max cap + equal-split; F4).
- D8 convergence rule false negative → REPLACED by deterministic KL stopping rule (F13 shows the iteration is trivial).
- D9 sqrt(count) downweight → REMOVED, replaced by equal-split clustering.
- D10 fabricated gate confidence → REMOVED (not carried into the implementation).
- D11 false "zero stubs" / broken imports → NOT applicable to the new implementation (stdlib, no external imports).
- D12 vacuous tests → REPLACED by F1–F13 (executable falsifiers).
- D13 "quantum" terminology → DROPPED.
- D14 patent novelty overclaim → still not adjudicated (UNVERIFIED).
- D15 multiple incompatible canonical forms → RESOLVED for the go-forward path: one implementation, one spec.

## 6. Remaining gap (Vessel Q22, restated for Wave 03)

The provenance key is only as good as the fields supplied. If IntelAMP does not actually
populate `model_family` / `evidence_root_digest` / `context_digest` / `prompt_lineage_digest`
with true values, the cluster key silently degrades to "all distinct" and correlated error
survives. The LINEAGE_UNKNOWN failure class exists but is not yet enforced by any caller.
This is the strongest remaining attack surface.

## 7. Unresolved / UNVERIFIED

- U1: no independent corroboration (0/66 mission vessels completed by cohorts).
- U2: parameters P_RESIDUAL, τ, θ, w_max, ε, N_CAL are declared and falsifier-constrained, not derived.
- U3: prior-art status of belief-distribution consensus not adjudicated.
- U4: F13 shows the round machinery is unnecessary — not yet removed from the wider lineage.
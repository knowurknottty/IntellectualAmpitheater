# QIPC WAVE 01 — COHORT DISCOVERY (pre-recursion artifact, artifact_0)

Status: INDEPENDENT-DISCOVERY stage. Produced by the tool-capable aggregator
(AGG-22). No prior wave artifact exists; nothing here is a challenge to a
predecessor. All repository claims below are OBSERVED (direct read/execution)
unless marked UNVERIFIED.

## 1. Lineage inventory (OBSERVED — bounded filesystem search)

Search roots: `~/biocapt-ecosystem`, `~/OGbiocapt`, `~/capt-node-workspace`.
All paths verified to exist unless noted.

Algorithmic (real belief-consensus code):

- `biocapt-ecosystem/capt/src/qipc.py` (444 lines) — **canonical amplitude form**. `QuantumBelief` holds complex amplitudes; `superpose()` = unsigned amplitude addition + renormalize; consensus when `min(node confidence) > 0.9`; `_check_agreement()` = mode of argmax. Class docstring claims "O(log n) messages".
- `OGbiocapt/modules/qipc_mobile.py` (805 lines) — **log-product form**. `BeliefState.merge` = weighted log-product (product-of-experts) with `max(p,1e-12)` floor; KL-divergence convergence; per-node `reliability` + `calibration_history`; `source_tag` correlation flag; conditional consensus gate ("Uber Ouroboros"); `get_consensus_result()` = reliability-weighted log-product with `sqrt(count)` correlated-source downweight.
- `biocapt-ecosystem/primary/biocapt-desktop/modules/qipc_mobile.py` and `.../backend/biocapt/modules.bak.REMOVED/qipc_mobile.py` — additional copies/forks of the above.
- `biocapt-ecosystem/primary/biocapt-desktop/src/captlang/qipc.captlang` — **product-rule form** with a "Ricci Flow convergence d_g/dt = -2*Ric(g)" comment; header forbids changing product→average.
- `biocapt-ecosystem/primary/biocapt-desktop/fastlibs/fast_qipc.pyx|.c|.html` and `secondary/biocapt-v2-android/fastlibs/fast_qipc.*` (incl. a compiled `.so`) — Cython fast-entropy accelerators for the above.

Wrappers / integration:

- `OGbiocapt/modules_extras_openclaw_v21/frankencapt_qipc_module.py` (100 lines) — BaseModule wrapper around `QIPCMobile`.
- `biocapt-ecosystem/frankencapt/frankencapt-base/core/qipc/__init__.py` — import wrapper pointing at `/root/.openclaw/workspace/biocapt-v2-desktop` (**path does not exist on this host** → import would fail).
- `biocapt-ecosystem/frankencapt/modules/qipc/` — empty (only `__pycache__`).

Claimed-but-degenerate:

- `biocapt-ecosystem/unified_modules/qipc_module.py` (96 lines) — `QipcModule.process()` returns `output: None` with a `# TODO`. Header claims "zero stub functions". **FALSE.**
- `OGbiocapt/modules_extras_openclaw_v21/qipc_module.py` (278 lines) — adds VQE/qiskit circuit code; but `QipcModule.process()` also `# TODO` → `output: None`; header claims "zero stubs". **FALSE.** Imports `from quantum_inspired import QuantumConsensus` after inserting `~/biocapt-ecosystem` on `sys.path`; **`quantum_inspired.py` does not exist there** → import fails.

Governance / paper trail:

- `biocapt-ecosystem/capt/patents/PATENT_QIPC_WORKING_DRAFT.md`, `PATENT_03_QIPC_Q_DRAFT.md` — patent application drafts; background section asserts "No existing approach uses probability distributions to represent beliefs". (Prior art: log-linear/opinion pooling and product-of-experts predate this; the assertion is not established here → UNVERIFIED/overclaim.)
- `biocapt-ecosystem/capt/tests/test_qipc.py` (55 lines) — assertions are `"consensus_reached" in result` and `isinstance(result, dict)`. **Vacuous.**
- `capt/qasm_circuits/qipc_q.qasm`, `capt/originq_hardware_qasm/02_qipc_q.qasm`, `capt/originq_result_QIPC-Q.json` — hardware-QASM artifacts, disconnected from the consensus algorithm above (no code path reads them).

Conclusion: no single source of truth. At least four mutually-incompatible mathematical forms (amplitude add / log-product / product-rule / stub) exist under the same name, with divergent convergence rules and two broken imports.

## 2. Empirical falsification (OBSERVED — real execution)

Harness: `experiments/qipc_falsifier.py`, run with `uv run --python 3.12 --with numpy python`.
Canonical module executes only on Python >= 3.10 (fails to import on 3.9 and on the 3.14 backend venv — `dataclass(slots=True)` and missing numpy).
Raw receipts: `experiments/receipts.json`.

- E1 reproducibility — same input, 40 runs → **2 distinct outcomes** (argmax A vs B), consensus never reached. NON_REPRODUCIBLE.
- E2 destructive interference — two opposite certain beliefs → uniform 0.5/0.5, confidence 0.0, argmax arbitrary ("A"); agreement `null`. Genuine disagreement is annihilated.
- E3 false-consensus metric — maximally uncertain 50/50 posterior → `_check_agreement()` = **1.0 (100% agreement)**. The agreement metric is decoupled from the belief mass.
- E4 Byzantine — one source with amplitude 5.0 against six honest "A" voters did not flip the argmax here, but the merge ratio shows source influence is carried by **raw amplitude magnitude, not count/weight** — unbounded influence in principle; no reliability/cap/quarantine in the canonical form.
- E5 cost — messages 30/100/250/600 at n=10/25/50/100 (fully connected). O(n log n) per round holds; the "saving" is claimed only against a strawman O(n²) broadcast.
- E6 algebra — `superpose` is commutative and idempotent after renorm, but is **not a probability merge**: unsigned amplitude addition destroys information on sign disagreement (E2).

## 3. Cross-variant defect ledger

| id | defect | variants affected | severity | evidence |
| --- | --- | --- | --- | --- |
| D1 | non-reproducible (unseeded RNG gossip + random measurement) | qipc.py; qipc_mobile.py | HIGH | E1 |
| D2 | destructive interference annihilates disagreement → arbitrary argmax | qipc.py | HIGH | E2 |
| D3 | agreement metric decoupled from mass (reports 1.0 on a tie) | qipc.py; qipc_mobile `_calculate_agreement` | HIGH | E3 |
| D4 | no correlation model (shared model family / evidence root) | ALL algorithmic variants | HIGH | code read |
| D5 | reliability never closed (no ground-truth update loop called) | qipc_mobile (loop exists, uncalled) | HIGH | code read |
| D6 | minority erased by point-estimate / argmax reporting | ALL | MEDIUM | code read |
| D7 | influence unbounded by count; no cap/quarantine | qipc.py; qipc_mobile | HIGH | E4 |
| D8 | convergence rule `min conf > 0.9` → false negative on splits | qipc.py | MEDIUM | E1/E2 |
| D9 | ad-hoc `sqrt(count)` correlation downweight with no derivation | qipc_mobile.get_consensus_result | MEDIUM | code read |
| D10 | fabricated confidence on gate-skip: `maybe_consensus` returns `consensus_reached: True`, `final_confidence: 0.75` | qipc_mobile | HIGH (integrity) | code read |
| D11 | "zero stubs" claims false; `process()` returns None; two broken imports | unified + openclaw `qipc_module.py`; frankencapt core wrapper | HIGH (integrity) | code read |
| D12 | vacuous tests | test_qipc.py | HIGH (assurance) | code read |
| D13 | "quantum" terminology retained without mechanism | all naming + patent drafts | MEDIUM (epistemics) | code read |
| D14 | patent background overclaims novelty of belief-distribution consensus | patent drafts | MEDIUM | code read |
| D15 | multiple incompatible canonical forms under one name | whole lineage | HIGH (architecture) | lineage inventory |

## 4. The gap every variant misses (Vessel Q22)

**All known variants fuse point beliefs and never model correlated error at the level that actually matters — shared provenance.** The only correlation signals present are a user-supplied `source_tag` (qipc_mobile) and an unterivated `sqrt(count)` downweight. No variant reasons about the two dominant real-world correlation sources: (a) shared model family / training lineage, (b) shared evidence root. Because of this, N panes that all read the same source and run on the same family produce a posterior that sharpens as if N independent measurements had occurred — the exact false-consensus failure the mission targets. Compounding it: reliability is never calibrated (D5), results are not reproducible (D1), and minority mass is erased (D6).

## 5. Dispositions (AGG-22)

All 22 lenses `completed`, evidence = sections 1–4 and the executed harness.
Cohort-level dispositions for the three reference cohorts: recorded in RUN_MANIFEST
(no usable independent artifact; 63 starved, 3 invalidated, 0 completed).

## 6. Unresolved / UNVERIFIED

- U1: the intended aggregator preset's exact weights are not independently observable.
- U2: prior-art status of "belief-distribution consensus" is not adjudicated here.
- U3: qasm quantum artifacts are not connected to any executed code path (UNVERIFIED whether ever used).
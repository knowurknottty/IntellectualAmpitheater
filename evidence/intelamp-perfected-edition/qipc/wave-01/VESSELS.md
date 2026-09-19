# QIPC WAVE 01 — 22 VESSEL LENSES

A Vessel is a logical error-seeking lens, not a persona and not a provider call.
Each lens below was applied by the tool-capable aggregator (AGG-22). The three
tool-blind reference cohorts could not execute theirs (all `starved`/`invalidated`;
see RUN_MANIFEST). Dispositions refer to the aggregator's pass.

| # | vessel_id | domain lens | core question | attacks assumption | characteristic failure mode | evidence obligation | falsification criterion | expected output | disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Q01-math | probability theory | Is any of this real math? | "superposition = probability" | metaphor dressed as arithmetic | derive each op from a rule | an op that violates total probability | formal verdict | completed |
| 2 | Q02-algebra | abstract algebra | Do the merge ops form a sane algebra? | "interference is well-behaved" | non-associative / non-idempotent merge | op truth table | counterexample | algebra table | completed |
| 3 | Q03-calibration | decision theory | Are confidences calibrated? | "confidence means P(correct)" | miscalibrated certainty | reliability/Brier evidence | ECE not measurable | calibration verdict | completed |
| 4 | Q04-correlation | statistics | Is dependence modeled? | "N sources = N evidence" | correlated-error blindness | shared-root test | correlated sources sharpen posterior | correlation audit | completed |
| 5 | Q05-order | distributed systems | Does input order change output? | "merge is order-free" | non-determinism | rerun matrix | >1 distinct outcome | determinism receipt | completed |
| 6 | Q06-overconf | information theory | Does certainty inflate? | "agreement = confidence" | entropy collapse | entropy trace | conf rises with ties | entropy audit | completed |
| 7 | Q07-falsecons | social epistemology | Can it manufacture consensus? | "agreement metric is honest" | agreement decoupled from mass | metric trace | agreement=1 at max entropy | metric audit | completed |
| 8 | Q08-minority | adversarial reasoning | Is dissent preserved? | "argmax reports the truth" | minority erasure | dissent mass check | losing mass dropped silently | dissent report | completed |
| 9 | Q09-byzantine | security | Can one node poison? | "influence ∝ count" | magnitude dominance | poison experiment | single node flips honest majority | poison receipt | completed |
| 10 | Q10-stale | systems | Does reliability decay/close? | "reliability is live" | stale weights | calibration-loop trace | no ground truth closes loop | staleness finding | completed |
| 11 | Q11-provenance | data lineage | Can a result be traced? | "answer is enough" | provenance loss | digest/source check | no source lineage retained | lineage audit | completed |
| 12 | Q12-gossip | distributed systems | Do gossip paths matter? | "topology-neutral" | topology-dependent outcome | topology matrix | result changes with topology | pathology report | completed |
| 13 | Q13-converge | analysis | Is the stopping rule sound? | "confidence>0.9 = consensus" | false negative/positive | rule replay | split never converges | stopping-rule audit | completed |
| 14 | Q14-cost | algorithms | Real cost? | "O(n log n) wins" | strawman baseline | message/time counters | cost worse in practice | cost receipt | completed |
| 15 | Q15-replay | reproducibility | Replayable? | "runs reproduce" | hidden RNG | seed/capture check | unseeded RNG | replay verdict | completed |
| 16 | Q16-boundary | systems governance | Advisory or authority? | "consensus decides" | advisory laundered as verdict | authority map | output used as verification | boundary audit | completed |
| 17 | Q17-quantum | physics/epistemics | Is "quantum" earned? | "quantum-inspired is real" | branding over substance | claim/mechanism split | term retained w/o mechanism | terminology verdict | completed |
| 18 | Q18-impl | software integrity | Is the code what it claims? | "zero stubs" | stub/import rot | source read + import | import fails / TODO returns None | implementation audit | completed |
| 19 | Q19-tests | test theory | Do tests falsify? | "tests prove correctness" | vacuous assertions | test read | assert isinstance only | test-quality verdict | completed |
| 20 | Q20-integrate | systems | Does it fit CAPT? | "drop-in protocol" | covert coupling | interface map | no clean boundary | integration verdict | completed |
| 21 | Q21-simplify | engineering | What is the minimal core? | "all machinery needed" | complexity theater | necessity proof per op | op removable w/o loss | simplification plan | completed |
| 22 | Q22-gap | novel systems | What failure do ALL variants miss? | "the lineage is complete" | unfound blind spot | cross-variant diff | a gap present in every variant | gap statement + mechanism | completed |
"""
Extended adversarial falsifiers F9-F12 for QIPC-HYBRID-vNEXT.
Attacks the implementation harder than F1-F8. Real execution, no fabrication.
Run: python3 qipc_hybrid_falsifier_ext.py
"""
from __future__ import annotations

import json
import random

from qipc_hybrid import OPEN, Provenance, Source, fuse, fuse_iterated


def prov(sid, family="f", ev="e", ctx="c", lin="l"):
    return Provenance(sid, "m", family, ev, ctx, lin)


def H(*n):
    return list(n)


def F9_correlated_majority_vs_independent_minority():
    """5 sources sharing ONE provenance key vs 2 independent sources.
    The 5 are effectively one vote (cluster), so a coherent independent
    minority must be able to compete — the whole point of the firewall."""
    correlated = [
        Source({"A": 0.9, "B": 0.1}, 0.9, prov(f"c{i}", family="FAM", ev="SAME", ctx="C", lin="L"))
        for i in range(5)
    ]
    independent = [
        Source({"A": 0.2, "B": 0.8}, 0.9, prov("i1", family="X", ev="r1")),
        Source({"A": 0.3, "B": 0.7}, 0.9, prov("i2", family="Y", ev="r2")),
    ]
    r = fuse(correlated + independent, H("A", "B", OPEN))
    return {"test": "F9_correlated_majority_vs_independent_minority",
            "posterior": r.posterior, "independence_status": r.independence_status,
            "clusters": r.clusters, "argmax": max(r.posterior, key=r.posterior.get),
            "pass": max(r.posterior, key=r.posterior.get) == "B"}


def F10_many_identical_sources_bounded():
    """k identical-provenance sources must add NO more confidence than one."""
    def conf(k):
        srcs = [Source({"A": 0.9, "B": 0.1}, 0.9, prov(f"s{i}", family="F", ev="E", ctx="C", lin="L"))
                for i in range(k)]
        return fuse(srcs, H("A", "B", OPEN)).posterior["A"]
    c1, c10 = conf(1), conf(10)
    return {"test": "F10_many_identical_sources_bounded", "conf_1": c1, "conf_10": c10,
            "pass": abs(c10 - c1) < 1e-6}


def F11_open_world_mass():
    """Is the open-world residual more than an epsilon artifact?"""
    srcs = [
        Source({"A": 0.6, "B": 0.4}, 0.9, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.4, "B": 0.6}, 0.9, prov("s1", family="f1", ev="e1")),
    ]
    r = fuse(srcs, H("A", "B", "C_hypothesis_nobody_proposed", OPEN))
    novel = r.posterior["C_hypothesis_nobody_proposed"]
    return {"test": "F11_open_world_mass", "posterior": r.posterior, "novel_mass": novel,
            "pass": novel > 0.05,
            "note": "If novel_mass ~ epsilon, the open-world claim is technically true but practically false."}


def F12_quarantine_order_invariance():
    """Quarantine set and posterior must be invariant to source order."""
    base = [
        Source({"A": 0.9, "B": 0.1}, 0.9, prov(f"h{i}", family=f"f{i}", ev=f"e{i}")) for i in range(5)
    ]
    base.append(Source({"A": 0.001, "B": 0.999}, 1.0, prov("poison", family="P", ev="PE")))
    ref = fuse(base, H("A", "B", OPEN))
    ok = True
    for _ in range(10):
        s = base[:]
        random.shuffle(s)
        r = fuse(s, H("A", "B", OPEN))
        if r.posterior != ref.posterior or sorted(r.quarantined) != sorted(ref.quarantined):
            ok = False
    return {"test": "F12_quarantine_order_invariance", "pass": ok,
            "quarantined": ref.quarantined}


def F13_iteration_is_a_noop():
    """Is fuse_iterated actually iterative belief propagation, or a one-shot?"""
    srcs = [
        Source({"A": 0.7, "B": 0.3}, 0.8, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.3, "B": 0.7}, 0.8, prov("s1", family="f1", ev="e1")),
    ]
    it = fuse_iterated(srcs, H("A", "B", OPEN), max_passes=5)
    one = fuse(srcs, H("A", "B", OPEN)).posterior
    return {"test": "F13_iteration_is_a_noop", "passes": it["passes"],
            "stopping_reason": it["stopping_reason"],
            "matches_single_shot": it["result"].posterior == one,
            "note": "If Fusion is stateless, 'rounds' are decorative. Honest finding, not a defect."}


def main():
    tests = [F9_correlated_majority_vs_independent_minority(), F10_many_identical_sources_bounded(),
             F11_open_world_mass(), F12_quarantine_order_invariance(), F13_iteration_is_a_noop()]
    print(json.dumps({"suite": "F9-F13", "results": tests}, indent=2))


if __name__ == "__main__":
    main()
"""
Falsifier suite F1-F8 for QIPC-HYBRID-vNEXT (qipc_hybrid.py).
Every result below is produced by executing the real implementation.
Run: python3 qipc_hybrid_falsifier.py   (stdlib only)
"""
from __future__ import annotations

import json
import random

from qipc_hybrid import OPEN, Provenance, Source, confidence, fuse, fuse_iterated


def prov(sid, family="famA", ev="ev1", ctx="ctx1", lin="lin1"):
    return Provenance(sid, "model-x", family, ev, ctx, lin)


def H(*names):
    return list(names)


def F1_reproducibility(runs=40):
    srcs = [
        Source({"A": 0.8, "B": 0.2}, 0.9, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.2, "B": 0.8}, 0.9, prov("s1", family="f1", ev="e1")),
        Source({"A": 0.6, "B": 0.4}, 0.7, prov("s2", family="f2", ev="e2")),
    ]
    outs = set()
    for _ in range(runs):
        r = fuse(srcs, H("A", "B", OPEN))
        outs.add(tuple(sorted(r.posterior.items())))
    return {"test": "F1_reproducibility", "runs": runs, "distinct_outcomes": len(outs),
            "pass": len(outs) == 1}


def F2_no_annihilation():
    srcs = [
        Source({"A": 1.0, "B": 0.0}, 0.9, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.0, "B": 1.0}, 0.9, prov("s1", family="f1", ev="e1")),
    ]
    r = fuse(srcs, H("A", "B", OPEN))
    both_retained = r.posterior["A"] > 0.05 and r.posterior["B"] > 0.05
    return {"test": "F2_no_annihilation", "posterior": r.posterior,
            "dissent_reported": len(r.dissent) > 0,
            "pass": both_retained and len(r.dissent) > 0}


def F3_cluster_discount():
    one = [Source({"A": 0.95, "B": 0.05}, 0.9, prov("s0", family="f0", ev="e0"))]
    two = [
        Source({"A": 0.95, "B": 0.05}, 0.9, prov("a", family="f0", ev="e0")),
        Source({"A": 0.95, "B": 0.05}, 0.9, prov("b", family="f0", ev="e0")),
    ]
    r1 = fuse(one, H("A", "B", OPEN))
    r2 = fuse(two, H("A", "B", OPEN))
    sharpen = r2.posterior["A"] - r1.posterior["A"]
    return {"test": "F3_cluster_discount", "one_source": r1.posterior["A"],
            "two_identical": r2.posterior["A"], "sharpen_delta": round(sharpen, 6),
            "pass": sharpen < 1e-6}


def F4_byzantine_bound():
    srcs = [Source({"A": 0.999, "B": 0.001}, 0.9, prov(f"h{i}", family=f"f{i}", ev=f"e{i}"))
            for i in range(6)]
    srcs.append(Source({"A": 0.001, "B": 0.999}, 1.0, prov("poison", family="fp", ev="ep")))
    r = fuse(srcs, H("A", "B", OPEN))
    return {"test": "F4_byzantine_bound", "posterior": r.posterior,
            "argmax": max(r.posterior, key=r.posterior.get),
            "quarantined": r.quarantined,
            "pass": max(r.posterior, key=r.posterior.get) == "A"}


def F5_calibration_loop():
    s = Source({"A": 0.6, "B": 0.4}, 0.9, prov("s0"))
    r0 = fuse([s], H("A", "B", OPEN)).weights["s0"]
    for _ in range(20):
        s.record_outcome("A", ["A", "B"])
    r1 = fuse([s], H("A", "B", OPEN)).weights["s0"]
    return {"test": "F5_calibration_loop", "weight_uncalibrated": r0,
            "weight_after_20": r1, "calibrated": s.calibrated,
            "pass": (not s.calibrated) is False and r0 <= 0.5 and r1 > 0.5}


def F6_dissent():
    srcs = [
        Source({"A": 0.7, "B": 0.2, "C": 0.1}, 0.9, prov("m1", family="f1", ev="e1")),
        Source({"A": 0.7, "B": 0.2, "C": 0.1}, 0.9, prov("m2", family="f2", ev="e2")),
        Source({"A": 0.1, "B": 0.8, "C": 0.1}, 0.9, prov("min", family="f3", ev="e3")),
    ]
    r = fuse(srcs, H("A", "B", "C", OPEN))
    return {"test": "F6_dissent", "argmax": max(r.posterior, key=r.posterior.get),
            "minority_mass_B": r.posterior["B"], "dissent": r.dissent,
            "pass": r.posterior["B"] > 0.05 and len(r.dissent) > 0}


def F7_order_invariance():
    base = [
        Source({"A": 0.8, "B": 0.2}, 0.9, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.3, "B": 0.7}, 0.8, prov("s1", family="f1", ev="e1")),
        Source({"A": 0.6, "B": 0.4}, 0.6, prov("s2", family="f2", ev="e2")),
        Source({"A": 0.5, "B": 0.5}, 0.5, prov("s3", family="f3", ev="e3")),
    ]
    ref = fuse(base, H("A", "B", OPEN)).posterior
    ok = True
    for _ in range(10):
        shuffled = base[:]
        random.shuffle(shuffled)
        if fuse(shuffled, H("A", "B", OPEN)).posterior != ref:
            ok = False
    return {"test": "F7_order_invariance", "pass": ok, "posterior": ref}


def F8_open_world():
    # hypothesis "D" appears in NO source support
    srcs = [
        Source({"A": 0.6, "B": 0.4}, 0.9, prov("s0", family="f0", ev="e0")),
        Source({"A": 0.4, "B": 0.6}, 0.9, prov("s1", family="f1", ev="e1")),
    ]
    r = fuse(srcs, H("A", "B", "D", OPEN))
    return {"test": "F8_open_world", "posterior": r.posterior,
            "D_mass": r.posterior["D"],
            "pass": r.posterior["D"] > 0.0}


def main():
    tests = [F1_reproducibility(), F2_no_annihilation(), F3_cluster_discount(),
             F4_byzantine_bound(), F5_calibration_loop(), F6_dissent(),
             F7_order_invariance(), F8_open_world()]
    passed = sum(1 for t in tests if t["pass"])
    print(json.dumps({"suite": "F1-F8", "passed": passed, "total": len(tests),
                      "results": tests}, indent=2))


if __name__ == "__main__":
    main()
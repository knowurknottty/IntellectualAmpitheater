"""
QIPC WAVE 03 — adversarial suite.

Re-runs the wave-02 falsifiers F1-F13 against the wave-03 implementation
(qipc_hybrid_v3.py), then adds:
  F14  honest strong dissent must NOT be excluded (wave-03 repair target)
  F15  malformed posteriors must be rejected fail-closed

The wave-02 suites are loaded with qipc_hybrid_v3 registered under the module
name 'qipc_hybrid', so their `from qipc_hybrid import ...` binds to v3.
Run: python3 wave03_suite.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


v3 = _load("qipc_hybrid", D / "qipc_hybrid_v3.py")          # shadows the wave-02 module
f1 = _load("_f1", D / "_f1.py")
f2 = _load("_f2", D / "_f2.py")

Provenance, Source, fuse = v3.Provenance, v3.Source, v3.fuse


def _prov(sid, fam):
    return Provenance(sid, "m", fam, "e", "c", "l")


def F14_honest_dissent_not_excluded():
    """The wave-02 defect: an honest strong dissenter sat at ~3.516 nats > theta
    and was quarantined. It must now stay IN the fusion and be reported."""
    srcs = [Source({"A": 0.9, "B": 0.1}, 0.9, _prov(f"h{i}", f"fam{i}")) for i in range(5)]
    srcs.append(Source({"A": 0.1, "B": 0.9}, 0.9, _prov("diss", "famD")))
    r = fuse(srcs, ["A", "B", v3.OPEN])
    diss = [d for d in r.dissent if "diss" in d["sources"]]
    return {
        "test": "F14_honest_dissent_not_excluded",
        "posterior": r.posterior,
        "rejected": r.rejected,
        "outliers": r.outliers,
        "dissent_reported": len(diss) > 0,
        "dissent_kept_in_fusion": all(not d["rejected"] for d in diss),
        "pass": ("diss" not in r.rejected) and len(diss) > 0,
    }


def F15_malformed_rejected():
    """A malformed posterior (sum != 1) must be rejected fail-closed."""
    srcs = [
        Source({"A": 0.6, "B": 0.4}, 0.9, _prov("ok1", "f1")),
        Source({"A": 0.6, "B": 0.6}, 0.9, _prov("bad_sum", "f2")),      # sums to 1.2
        Source({"A": -0.5, "B": 1.5}, 0.9, _prov("bad_neg", "f3")),     # negative mass
    ]
    r = fuse(srcs, ["A", "B", v3.OPEN])
    return {
        "test": "F15_malformed_rejected",
        "rejected": r.rejected,
        "posterior": r.posterior,
        "pass": set(r.rejected) == {"bad_sum", "bad_neg"},
    }


def main():
    tests = [
        f1.F1_reproducibility(), f1.F2_no_annihilation(), f1.F3_cluster_discount(),
        f1.F4_byzantine_bound(), f1.F5_calibration_loop(), f1.F6_dissent(),
        f1.F7_order_invariance(), f1.F8_open_world(),
        f2.F9_correlated_majority_vs_independent_minority(),
        f2.F10_many_identical_sources_bounded(), f2.F11_open_world_mass(),
        f2.F12_quarantine_order_invariance(), f2.F13_iteration_is_a_noop(),
        F14_honest_dissent_not_excluded(), F15_malformed_rejected(),
    ]
    graded = [t for t in tests if "pass" in t]
    passed = sum(1 for t in graded if t["pass"])
    print(json.dumps({
        "suite": "wave-03 F1-F15 (v3)",
        "graded_passed": passed, "graded_total": len(graded),
        "informational": [t["test"] for t in tests if "pass" not in t],
        "results": tests,
    }, indent=2))


if __name__ == "__main__":
    main()
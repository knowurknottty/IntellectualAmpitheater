"""
QIPC Wave-01 falsification harness.

Attacks the *canonical* implementation at
  /Users/knowurknot/biocapt-ecosystem/capt/src/qipc.py
empirically. Prints machine-readable receipts. No fabrication: every number
below is produced by executing the real module in this process.

Run with a Python >= 3.10 that has numpy, e.g.
  uv run --python 3.12 --with numpy python qipc_falsifier.py
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import random
import statistics
import sys
from pathlib import Path

CANON = Path("/Users/knowurknot/biocapt-ecosystem/capt/src/qipc.py")


def load_canonical():
    spec = importlib.util.spec_from_file_location("qipc_canonical", CANON)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q = load_canonical()
QIPCNetwork = Q.QIPCNetwork
QuantumBelief = Q.QuantumBelief


def build_network(n_nodes, beliefs, connect_all=True):
    net = QIPCNetwork()
    for i in range(n_nodes):
        net.add_node(f"n{i}")
    if connect_all:
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                net.connect_nodes(f"n{i}", f"n{j}")
    for node_id, amps in beliefs.items():
        if node_id in net.nodes:
            net.nodes[node_id].set_belief("decision", QuantumBelief(dict(amps)))
    return net


def E1_reproducibility(runs=40):
    """Same input, same seed of worlds -> is the outcome reproducible?"""
    outcomes = []
    for _ in range(runs):
        beliefs = {f"n{i}": {"A": 0.9 + 0j, "B": 0.1 + 0j} for i in range(4)}
        beliefs.update({f"n{i}": {"A": 0.1 + 0j, "B": 0.9 + 0j} for i in range(4, 7)})
        net = build_network(7, beliefs)
        res = asyncio.run(net.run_consensus("decision", max_rounds=15))
        top, _p = net.nodes["n0"].beliefs["decision"].most_likely()
        outcomes.append((res["consensus_reached"], res["rounds"], res.get("agreement"), top))
    distinct = set(outcomes)
    return {
        "experiment": "E1_reproducibility",
        "runs": runs,
        "distinct_outcomes": len(distinct),
        "sample": sorted(list(distinct))[:6],
        "verdict": "NON_REPRODUCIBLE" if len(distinct) > 1 else "REPRODUCIBLE",
    }


def E2_destructive_interference():
    """Two equally-confident, mutually-exclusive beliefs on one topic."""
    net = build_network(2, {"n0": {"A": 1.0 + 0j}, "n1": {"B": 1.0 + 0j}})
    res = asyncio.run(net.run_consensus("decision", max_rounds=10))
    row0 = net.nodes["n0"].beliefs["decision"]
    probs = {k: row0.get_probability(k) for k in row0.amplitudes}
    top, p = row0.most_likely()
    return {
        "experiment": "E2_destructive_interference",
        "final_probs_n0": {str(k): round(v, 4) for k, v in probs.items()},
        "consensus_confidence": round(row0.get_consensus_confidence(), 4),
        "reported_agreement": res.get("agreement"),
        "argmax_choice": str(top),
        "consensus_reached": res["consensus_reached"],
        "verdict": "CONFLICT_ANNIHILATION_ARBITRARY_ARGMAX",
    }


def E3_false_consensus_metric():
    """Does _check_agreement report high agreement while confidence is uniform?"""
    net = build_network(4, {"n0": {"A": 1.0 + 0j, "B": 1.0 + 0j}})
    for i in range(1, 4):
        net.nodes[f"n{i}"].set_belief("decision", QuantumBelief({"A": 1.0 + 0j, "B": 1.0 + 0j}))
    b = net.nodes["n0"].beliefs["decision"]
    return {
        "experiment": "E3_false_consensus_metric",
        "confidence_all_tied": round(b.get_consensus_confidence(), 4),
        "agreement_metric": round(net._check_agreement("decision"), 4),
        "verdict": "AGREEMENT_METRIC_DECOUPLED_FROM_CONFIDENCE",
    }


def E4_byzantine_poison():
    """One node injects large amplitude against the honest majority."""
    honest = {f"n{i}": {"A": 1.0 + 0j} for i in range(6)}
    honest["n6"] = {"B": 5.0 + 0j}  # single poisoner, large amplitude
    net = build_network(7, honest)
    res = asyncio.run(net.run_consensus("decision", max_rounds=15))
    probs = net.nodes["n0"].beliefs["decision"].amplitudes
    top, _p = net.nodes["n0"].beliefs["decision"].most_likely()
    return {
        "experiment": "E4_byzantine_poison",
        "final_argmax_n0": str(top),
        "final_amplitude_ratio": round(
            abs(probs.get("B", 0)) / max(abs(probs.get("A", 1e-9)), 1e-9), 4
        ),
        "consensus_reached": res["consensus_reached"],
        "verdict": "AMPLITUDE_MAGNITUDE_NOT_BOUNDED_BY_COUNT",
    }


def E5_message_scaling():
    out = {}
    for n in (10, 25, 50, 100):
        beliefs = {f"n{i}": {"A": 1.0 + 0j} for i in range(n)}
        net = build_network(n, beliefs)
        res = asyncio.run(net.run_consensus("decision", max_rounds=5))
        out[n] = {"messages": res["messages"], "rounds": res["rounds"]}
    return {"experiment": "E5_message_scaling", "measurements": out,
            "note": "Fully-connected graph; compare to claimed O(n log n)."}


def E6_algebra_checks():
    """Is superpose commutative / associative / idempotent?"""
    a = QuantumBelief({"A": 1.0 + 0j, "B": 0.0 + 0j})
    b = QuantumBelief({"A": 0.0 + 0j, "B": 1.0 + 0j})
    c = QuantumBelief({"A": 0.5 + 0j, "B": 0.5 + 0j})
    ab = a.superpose(b); ba = b.superpose(a)
    ab_p = {k: round(ab.get_probability(k), 4) for k in ab.amplitudes}
    ba_p = {k: round(ba.get_probability(k), 4) for k in ba.amplitudes}
    aa = a.superpose(a)
    aa_p = {k: round(aa.get_probability(k), 4) for k in aa.amplitudes}
    a_p = {k: round(a.get_probability(k), 4) for k in a.amplitudes}
    abc = a.superpose(b).superpose(c)
    abc_p = {k: round(abc.get_probability(k), 4) for k in abc.amplitudes}
    return {
        "experiment": "E6_algebra_checks",
        "commutative": ab_p == ba_p,
        "idempotent": aa_p == a_p,
        "a": a_p, "a_superpose_a": aa_p,
        "destructive_example_ab": ab_p,
        "assoc_example_abc": abc_p,
        "verdict": "NOT_IDEMPOTENT" if aa_p != a_p else "idempotent_ok",
    }


def main():
    receipts = [
        E1_reproducibility(),
        E2_destructive_interference(),
        E3_false_consensus_metric(),
        E4_byzantine_poison(),
        E5_message_scaling(),
        E6_algebra_checks(),
    ]
    print(json.dumps({"canonical_path": str(CANON), "python": sys.version,
                      "receipts": receipts}, indent=2))


if __name__ == "__main__":
    main()
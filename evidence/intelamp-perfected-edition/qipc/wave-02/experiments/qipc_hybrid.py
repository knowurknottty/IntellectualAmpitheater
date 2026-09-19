"""
QIPC-HYBRID-vNEXT — reference implementation of qipc/wave-01/CANONICAL.md.

Stdlib only. Diagnostics-only surface: this module is an ADVISORY analyzer over
source beliefs + provenance. It has NO authority and NO execution capability.

Wave-02 change vs the wave-01 canonical text:
  The canonical proposed w_i = r_i / (1 + (k_c-1)*rho). That parameterization
  allows partial double-counting of correlated sources for any rho < 1 and also
  proved awkward to satisfy F3 exactly. This implementation RETIRES rho in favour
  of an equal-split rule inside a provenance cluster:
        w_i = min(w_max, r_i / k_c)
  so that a cluster of k identical-provenance sources contributes the weight of
  AT MOST one source (sum_i w_i = mean r for the cluster). This is conservative
  and provably satisfies F3. Recorded as an accepted change in wave-02.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any

EPS = 1e-6
W_MAX = 1.0
TAU = 0.01
THETA = 3.0
R_UNCAL = 0.5
N_CAL = 20
OPEN = "__open__"
P_RESIDUAL = 0.05  # open-world prior mass (wave-02 change 3)

FAILURE_CLASSES = (
    "ALL_UNCALIBRATED",
    "SINGLE_CLUSTER_NO_INDEPENDENCE",
    "DIVERGENT_NO_CONVERGENCE",
    "BYZANTINE_QUARANTINE",
    "EMPTY_SUPPORT",
    "LINEAGE_UNKNOWN",
)


@dataclass(frozen=True)
class Provenance:
    source_id: str
    model_id: str
    model_family: str
    evidence_root_digest: str
    context_digest: str
    prompt_lineage_digest: str
    adapter_version: str = "0"

    def key(self) -> str:
        payload = "\x1f".join(
            [
                self.model_family,
                self.evidence_root_digest,
                self.context_digest,
                self.prompt_lineage_digest,
                self.adapter_version,
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Source:
    posterior: dict[str, float]
    reliability: float
    provenance: Provenance
    calibrated: bool = False
    brier_history: list[float] = field(default_factory=list)

    def record_outcome(self, truth: str, hypotheses: list[str]) -> float:
        """Closed calibration loop: feed a resolved outcome."""
        brier = sum(
            (self.posterior.get(h, 0.0) - (1.0 if h == truth else 0.0)) ** 2
            for h in hypotheses
        )
        self.brier_history.append(brier)
        if len(self.brier_history) >= N_CAL:
            self.calibrated = True
        mean_brier = sum(self.brier_history) / len(self.brier_history)
        self.reliability = min(1.0, max(0.1, 1.0 / (1.0 + mean_brier)))
        return self.reliability


def _normalize(d: dict[str, float]) -> dict[str, float]:
    total = sum(d.values())
    if total <= 0:
        return {k: 0.0 for k in d}
    return {k: v / total for k, v in d.items()}


def _entropy(p: dict[str, float]) -> float:
    return -sum(v * math.log(v) for v in p.values() if v > 0)


def confidence(p: dict[str, float]) -> float:
    if len(p) <= 1:
        return 1.0
    h = _entropy(p)
    return max(0.0, min(1.0, 1.0 - h / math.log(len(p))))


def _symmetric_kl(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    out = 0.0
    for k in keys:
        pk = max(p.get(k, 0.0), EPS)
        qk = max(q.get(k, 0.0), EPS)
        out += pk * math.log(pk / qk) + qk * math.log(qk / pk)
    return out


@dataclass
class FusionResult:
    posterior: dict[str, float]
    confidence: float
    weights: dict[str, float]
    clusters: dict[str, list[str]]
    quarantined: list[str]
    dissent: list[dict[str, Any]]
    failure_classes: list[str]
    independence_status: str


def _default_prior(hypotheses: list[str], universe: list[str]) -> dict[str, float]:
    # The open-world residual is a SMALL prior mass, not a full competitor
    # hypothesis (wave-02 change 3). With a uniform prior over the universe, an
    # uncalibrated panel can never out-vote __open__, so no conclusion is ever
    # reachable — a defect exposed by F4/F9.
    enumerated = [h for h in universe if h != OPEN]
    share = (1.0 - P_RESIDUAL) / max(1, len(enumerated))
    prior = {h: share for h in enumerated}
    prior[OPEN] = P_RESIDUAL
    return prior


def fuse(
    sources: list[Source],
    hypotheses: list[str],
    prior: dict[str, float] | None = None,
    *,
    tau: float = TAU,
    theta: float = THETA,
) -> FusionResult:
    """Deterministic reliability-weighted log-linear pooling with provenance clustering."""
    universe = list(dict.fromkeys(list(hypotheses) + [OPEN]))
    if not sources:
        return FusionResult(
            posterior={h: (1.0 / len(universe)) for h in universe},
            confidence=0.0,
            weights={},
            clusters={},
            quarantined=[],
            dissent=[],
            failure_classes=["EMPTY_SUPPORT"],
            independence_status="none",
        )

    if prior is None:
        prior = _default_prior(hypotheses, universe)

    # --- clustering by provenance key ---
    clusters: dict[str, list[Source]] = {}
    for s in sources:
        clusters.setdefault(s.provenance.key(), []).append(s)

    # --- weights: equal split within a cluster, uncalibrated capped ---
    weights: dict[str, float] = {}
    for group in clusters.values():
        k = len(group)
        for s in group:
            r = min(s.reliability, R_UNCAL) if not s.calibrated else s.reliability
            weights[s.provenance.source_id] = min(W_MAX, r / k)

    def _fuse_with(active: list[Source]) -> dict[str, float]:
        # PARTIAL-INFORMATION POOLING (F11 repair):
        #   h IN a source's support           -> evidence: w * log(max(p, EPS))
        #   h ABSENT from a source's support  -> neutral: no contribution (the
        #       source has no opinion about an unproposed hypothesis; absence is
        #       NOT evidence against it). A source that wants to rule h out must
        #       list it explicitly with p=0.
        logp = {h: math.log(max(prior.get(h, EPS), EPS)) for h in universe}
        for s in active:
            w = weights[s.provenance.source_id]
            for h in universe:
                if h in s.posterior:
                    logp[h] += w * math.log(max(s.posterior[h], EPS))
        return _normalize({h: math.exp(v) for h, v in logp.items()})

    fused = _fuse_with(sources)

    def _source_distance(s: Source, fused: dict[str, float]) -> float:
        # Compare a source against the fused posterior ONLY on the hypotheses the
        # source actually opined about (support-restricted, renormalized). Using
        # the full universe wrongly quarantines every source whose support set is
        # smaller than the universe — a bug found by F4/F9 in wave 2.
        support = [h for h in universe if h in s.posterior]
        if not support:
            return 0.0
        p = _normalize({h: max(s.posterior[h], EPS) for h in support})
        q = _normalize({h: max(fused.get(h, 0.0), EPS) for h in support})
        return _symmetric_kl(p, q)

    # --- byzantine quarantine: source whose support-restricted KL to the fused posterior is an outlier ---
    quarantined: list[str] = []
    for s in sources:
        if _source_distance(s, fused) > theta:
            quarantined.append(s.provenance.source_id)

    active = [s for s in sources if s.provenance.source_id not in quarantined]
    if quarantined:
        fused = _fuse_with(active)

    # --- dissent: any cluster whose argmax differs from the fused argmax ---
    fused_argmax = max(fused, key=fused.get)
    dissent: list[dict[str, Any]] = []
    for key, group in clusters.items():
        cluster_posterior = _fuse_with(group)
        cmax = max(cluster_posterior, key=cluster_posterior.get)
        if cmax != fused_argmax:
            dissent.append(
                {
                    "cluster_key": key[:12],
                    "sources": [s.provenance.source_id for s in group],
                    "argmax": cmax,
                    "support": round(cluster_posterior.get(cmax, 0.0), 4),
                    "quarantined": any(
                        s.provenance.source_id in quarantined for s in group
                    ),
                }
            )

    # --- failure classes ---
    failures: list[str] = []
    if all(not s.calibrated for s in sources):
        failures.append("ALL_UNCALIBRATED")
    if len(clusters) == 1:
        failures.append("SINGLE_CLUSTER_NO_INDEPENDENCE")

    return FusionResult(
        posterior={h: round(v, 6) for h, v in fused.items()},
        confidence=round(confidence(fused), 6),
        weights={k: round(v, 6) for k, v in weights.items()},
        clusters={k[:12]: [s.provenance.source_id for s in g] for k, g in clusters.items()},
        quarantined=quarantined,
        dissent=dissent,
        failure_classes=failures,
        independence_status="single_cluster" if len(clusters) == 1 else f"{len(clusters)}_clusters",
    )


def fuse_iterated(
    sources: list[Source],
    hypotheses: list[str],
    *,
    max_passes: int = 10,
    tau: float = TAU,
) -> dict[str, Any]:
    """Deterministic incorporation with a KL stopping rule (§9/§10)."""
    prev = None
    history = []
    for p in range(1, max_passes + 1):
        res = fuse(sources, hypotheses)
        history.append(res.posterior)
        if prev is not None and _symmetric_kl(prev, res.posterior) < tau:
            res.failure_classes = list(res.failure_classes)
            return {
                "result": res,
                "passes": p,
                "stopping_reason": "converged",
                "history": history,
            }
        prev = res.posterior
    res = fuse(sources, hypotheses)
    res.failure_classes = list(res.failure_classes) + ["DIVERGENT_NO_CONVERGENCE"]
    return {"result": res, "passes": max_passes, "stopping_reason": "max_passes", "history": history}
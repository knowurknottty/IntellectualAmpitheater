"""Consensus Mirage Lint (advisory, exploratory).

Compares how many seats *agree* with how many *effective voices* stand
behind that agreement. When agreement outruns independence — the same
weights, or the same context, answering in chorus — the lint says so. It
never blocks, never fuses answers, never votes. Verdicts are lexical and
crude; the label travels with the output.
"""

from __future__ import annotations

from typing import Any

from .anchoring import text_similarity
from .voices import compute_effective_voices

ANSWER_SIMILARITY_THRESHOLD = 0.8


def _largest_agreement_cluster(outputs: list[str]) -> int:
    """Largest single-link cluster of near-identical answers."""
    parent = list(range(len(outputs)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            if text_similarity(outputs[i], outputs[j]) >= ANSWER_SIMILARITY_THRESHOLD:
                parent[find(i)] = find(j)
    sizes: dict[int, int] = {}
    for i in range(len(outputs)):
        sizes[find(i)] = sizes.get(find(i), 0) + 1
    return max(sizes.values(), default=0)


def mirage_lint(runs: list[dict[str, Any]], outputs: dict[str, str]) -> dict[str, Any]:
    """runs: completed-capable run dicts (see voices); outputs: run_id -> text."""
    voices = compute_effective_voices(runs)
    completed_outputs = [
        outputs[run["run_id"]]
        for run in runs
        if run.get("terminal_state") == "completed" and outputs.get(run["run_id"], "").strip()
    ]
    agreeing = _largest_agreement_cluster(completed_outputs) if completed_outputs else 0

    reasons: list[str] = []
    if len(completed_outputs) < 3:
        verdict = "insufficient_data"
        reasons.append("fewer than three completed answers; no consensus claim to lint")
    elif agreeing >= 2 and voices["effective_voices"] < agreeing:
        verdict = "mirage_risk"
        reasons.append(
            f"{agreeing} seats agree but only {voices['effective_voices']} effective voice(s) stand behind them"
        )
    else:
        verdict = "no_mirage_signal"
        reasons.append("agreement does not exceed the panel's effective independence")

    return {
        "verdict": verdict,
        "seats": voices["seats"],
        "completed": voices["completed"],
        "effective_voices": voices["effective_voices"],
        "agreeing_seats": agreeing,
        "similarity_threshold": ANSWER_SIMILARITY_THRESHOLD,
        "label": "exploratory: lexical agreement vs provenance independence; advisory only",
        "reasons": reasons,
    }

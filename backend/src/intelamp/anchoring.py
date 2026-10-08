"""Anchoring Delta: how far a seat moved toward its peers after reveal.

Exploratory measurement, labeled as such everywhere it surfaces. Movement
toward the majority is not correctness and not sycophancy proof; it is a
number a human can inspect next to the texts. Similarity is lexical
(difflib ratio over normalized text) — crude by design, honest by label.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

_WHITESPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text.strip().lower())


def text_similarity(a: str, b: str) -> float:
    a_norm, b_norm = normalize(a), normalize(b)
    if not a_norm and not b_norm:
        return 1.0
    if not a_norm or not b_norm:
        return 0.0
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def seat_anchor_report(
    *,
    seat_id: str,
    model_id: str,
    source_run_id: str,
    reveal_run_id: str | None,
    reveal_state: str | None,
    original: str,
    revised: str | None,
    peers_original: list[str],
) -> dict[str, Any]:
    """One seat's reveal measurement. `revised=None` until the reveal run ends."""
    report: dict[str, Any] = {
        "seat_id": seat_id,
        "model_id": model_id,
        "source_run_id": source_run_id,
        "reveal_run_id": reveal_run_id,
        "reveal_state": reveal_state,
        "self_similarity": None,
        "toward_majority_before": None,
        "toward_majority_after": None,
        "anchoring_delta": None,
    }
    if revised is None or not peers_original:
        return report
    before = sum(text_similarity(original, peer) for peer in peers_original) / len(peers_original)
    after = sum(text_similarity(revised, peer) for peer in peers_original) / len(peers_original)
    report["self_similarity"] = round(text_similarity(original, revised), 6)
    report["toward_majority_before"] = round(before, 6)
    report["toward_majority_after"] = round(after, 6)
    report["anchoring_delta"] = round(after - before, 6)
    return report

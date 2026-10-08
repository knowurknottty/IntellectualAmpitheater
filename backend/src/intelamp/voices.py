"""Effective Voices: independence-discounted panel counting.

A panel's agreement means little when the "voters" are the same weights
answering the same context twice. This module counts *effective* voices over
one dispatch: completed runs clustered by (model identity, exact context).
Two runs in one cluster are one voice — same model, same messages — however
many providers or seats carried them. Clusters sharing a model but not a
context stay separate voices and are flagged `shared_model`, because the
correlation is real but weaker. Unknown lineage is never merged: runs whose
context was not recorded keep their own cluster keyed by run.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


def _context_signature(messages: Any) -> str | None:
    if not isinstance(messages, list) or not messages:
        return None
    encoded = json.dumps(messages, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def compute_effective_voices(runs: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Cluster completed runs from one dispatch into effective voices.

    Each run mapping needs: run_id, seat_id, provider_id, model_id,
    terminal_state, context_messages (list or None).
    """
    runs = list(runs)
    completed = [run for run in runs if run.get("terminal_state") == "completed"]

    clusters: dict[str, dict[str, Any]] = {}
    for run in completed:
        signature = _context_signature(run.get("context_messages"))
        if signature is None:
            key = f"unrecorded:{run.get('run_id')}"
        else:
            key = f"{run.get('model_id')}|{signature}"
        cluster = clusters.setdefault(
            key,
            {
                "model_id": run.get("model_id"),
                "context_signature": signature,
                "provider_ids": set(),
                "seat_ids": [],
                "run_ids": [],
            },
        )
        cluster["provider_ids"].add(run.get("provider_id"))
        cluster["seat_ids"].append(run.get("seat_id"))
        cluster["run_ids"].append(run.get("run_id"))

    models_seen: dict[str, int] = {}
    for cluster in clusters.values():
        models_seen[cluster["model_id"]] = models_seen.get(cluster["model_id"], 0) + 1

    cluster_list = [
        {
            "model_id": cluster["model_id"],
            "context_signature": cluster["context_signature"],
            "provider_ids": sorted(pid for pid in cluster["provider_ids"] if pid),
            "seat_ids": cluster["seat_ids"],
            "run_ids": cluster["run_ids"],
            "shared_model": models_seen[cluster["model_id"]] > 1,
        }
        for cluster in clusters.values()
    ]
    cluster_list.sort(key=lambda c: (str(c["model_id"]), c["context_signature"] or ""))

    return {
        "seats": len(runs),
        "completed": len(completed),
        "effective_voices": len(cluster_list),
        "clusters": cluster_list,
    }

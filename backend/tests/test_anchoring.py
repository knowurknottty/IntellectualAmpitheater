from intelamp.anchoring import seat_anchor_report, text_similarity


def report(original, revised, peers):
    return seat_anchor_report(
        seat_id="s1",
        model_id="m1",
        source_run_id="r1",
        reveal_run_id="r2",
        reveal_state="completed",
        original=original,
        revised=revised,
        peers_original=peers,
    )


def test_identical_text_similarity_is_one():
    assert text_similarity("Same Answer", "same   answer") == 1.0
    assert text_similarity("", "") == 1.0
    assert text_similarity("x", "") == 0.0


def test_holding_answer_yields_zero_anchor_delta():
    result = report("my own view", "my own view", ["a different view entirely"])
    assert result["self_similarity"] == 1.0
    assert result["anchoring_delta"] == 0.0


def test_copying_peer_yields_positive_anchor_delta():
    result = report("totally unique alpha", "shared beta position", ["shared beta position"])
    assert result["anchoring_delta"] > 0.5
    assert result["toward_majority_after"] == 1.0


def test_pending_reveal_reports_nulls_not_zeros():
    result = seat_anchor_report(
        seat_id="s1",
        model_id="m1",
        source_run_id="r1",
        reveal_run_id="r2",
        reveal_state="running",
        original="x",
        revised=None,
        peers_original=["y"],
    )
    assert result["anchoring_delta"] is None
    assert result["reveal_state"] == "running"

from intelamp.mirage import mirage_lint

CTX = [{"role": "user", "content": "q"}]


def run(run_id, *, seat, provider, model, messages=CTX):
    return {
        "run_id": run_id,
        "seat_id": seat,
        "provider_id": provider,
        "model_id": model,
        "terminal_state": "completed",
        "context_messages": messages,
    }


def test_duplicated_model_agreement_is_mirage_risk():
    runs = [
        run("r1", seat="s1", provider="alias-a", model="same-weights"),
        run("r2", seat="s2", provider="alias-b", model="same-weights"),
        run("r3", seat="s3", provider="alias-c", model="same-weights"),
    ]
    outputs = {"r1": "the answer is x", "r2": "the answer is x", "r3": "the answer is x"}
    result = mirage_lint(runs, outputs)
    assert result["verdict"] == "mirage_risk"
    assert result["agreeing_seats"] == 3
    assert result["effective_voices"] == 1


def test_independent_models_agreeing_is_not_mirage():
    runs = [
        run("r1", seat="s1", provider="p1", model="model-a"),
        run("r2", seat="s2", provider="p2", model="model-b"),
        run("r3", seat="s3", provider="p3", model="model-c"),
    ]
    outputs = {"r1": "convergent finding", "r2": "convergent finding", "r3": "convergent finding"}
    result = mirage_lint(runs, outputs)
    assert result["verdict"] == "no_mirage_signal"
    assert result["effective_voices"] == 3


def test_two_seats_is_insufficient_data():
    runs = [
        run("r1", seat="s1", provider="p1", model="model-a"),
        run("r2", seat="s2", provider="p2", model="model-b"),
    ]
    outputs = {"r1": "x", "r2": "x"}
    result = mirage_lint(runs, outputs)
    assert result["verdict"] == "insufficient_data"


def test_disagreement_is_not_mirage():
    runs = [
        run("r1", seat="s1", provider="p1", model="same-weights"),
        run("r2", seat="s2", provider="p2", model="same-weights"),
        run("r3", seat="s3", provider="p3", model="same-weights"),
    ]
    outputs = {"r1": "alpha conclusion here", "r2": "completely other stance", "r3": "third unrelated position"}
    result = mirage_lint(runs, outputs)
    assert result["verdict"] == "no_mirage_signal"
    assert result["agreeing_seats"] == 1

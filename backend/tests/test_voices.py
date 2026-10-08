from intelamp.voices import compute_effective_voices

CTX_A = [{"role": "user", "content": "same question"}]
CTX_B = [{"role": "user", "content": "same question"}, {"role": "assistant", "content": "earlier"}]


def run(run_id, *, seat="s1", provider="p1", model="m1", state="completed", messages=CTX_A):
    return {
        "run_id": run_id,
        "seat_id": seat,
        "provider_id": provider,
        "model_id": model,
        "terminal_state": state,
        "context_messages": messages,
    }


def test_same_model_two_providers_same_context_is_one_voice():
    # Falsifier for Effective Voices: duplicate weights behind two provider
    # aliases must collapse to one effective voice.
    result = compute_effective_voices(
        [
            run("r1", seat="s1", provider="alias-a", model="qwen-local"),
            run("r2", seat="s2", provider="alias-b", model="qwen-local"),
        ]
    )
    assert result["seats"] == 2
    assert result["effective_voices"] == 1
    assert result["clusters"][0]["provider_ids"] == ["alias-a", "alias-b"]


def test_distinct_models_are_distinct_voices():
    result = compute_effective_voices(
        [
            run("r1", seat="s1", provider="p1", model="model-a"),
            run("r2", seat="s2", provider="p2", model="model-b"),
        ]
    )
    assert result["effective_voices"] == 2


def test_same_model_diverged_context_stays_two_voices_but_flagged():
    result = compute_effective_voices(
        [
            run("r1", seat="s1", model="m1", messages=CTX_A),
            run("r2", seat="s2", model="m1", messages=CTX_B),
        ]
    )
    assert result["effective_voices"] == 2
    assert all(cluster["shared_model"] for cluster in result["clusters"])


def test_failed_runs_cast_no_voice():
    result = compute_effective_voices(
        [
            run("r1", model="m1"),
            run("r2", seat="s2", model="m2", state="failed"),
        ]
    )
    assert result["completed"] == 1
    assert result["effective_voices"] == 1


def test_unrecorded_context_is_never_merged():
    result = compute_effective_voices(
        [
            run("r1", model="m1", messages=None),
            run("r2", seat="s2", model="m1", messages=None),
        ]
    )
    assert result["effective_voices"] == 2

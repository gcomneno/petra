from pet.irsr_state import (
    build_residual_state_progress_context,
    contextual_progress_score_by_structural_gain,
    contextual_progress_score_by_total_hint_delta,
    make_hostile_semiprime_residual_state,
    make_weighted_progress_scorer,
    summarize_residual_state_progress,
    try_seed_residual_state_slot_candidates,
)


def test_build_residual_state_progress_context_reports_before_after_and_progress():
    before = make_hostile_semiprime_residual_state(11413)
    after = try_seed_residual_state_slot_candidates(before, "a", [101])
    after["slots"][0]["pet_hints"]["near_generator"] = ["g1"]

    progress = summarize_residual_state_progress(before, after)
    context = build_residual_state_progress_context(before, after, progress)

    assert context == {
        "progress": {
            "candidate_count_delta": 1,
            "empty_slot_count_delta": -1,
            "branchable_slot_count_delta": 0,
            "payload_ready_changed": False,
            "entered_contradiction": False,
        },
        "before": {
            "candidate_count": 0,
            "empty_slot_count": 2,
            "branchable_slot_count": 0,
            "total_hint_count": 0,
            "payload_ready": False,
            "status": "open",
        },
        "after": {
            "candidate_count": 1,
            "empty_slot_count": 1,
            "branchable_slot_count": 0,
            "total_hint_count": 1,
            "payload_ready": False,
            "status": "open",
        },
    }


def test_contextual_progress_scorers_read_context_correctly():
    before = make_hostile_semiprime_residual_state(11413)
    after = try_seed_residual_state_slot_candidates(before, "a", [101])
    after["slots"][0]["pet_hints"]["near_generator"] = ["g1", "g2"]

    context = build_residual_state_progress_context(before, after)

    assert contextual_progress_score_by_structural_gain(context) == 9.0
    assert contextual_progress_score_by_total_hint_delta(context) == 2


def test_make_weighted_progress_scorer_combines_structural_and_hint_signal():
    before = make_hostile_semiprime_residual_state(11413)
    after = try_seed_residual_state_slot_candidates(before, "a", [101])
    after["slots"][0]["pet_hints"]["near_generator"] = ["g1", "g2"]

    context = build_residual_state_progress_context(before, after)

    scorer = make_weighted_progress_scorer(
        [
            (contextual_progress_score_by_structural_gain, 1.0),
            (contextual_progress_score_by_total_hint_delta, 10.0),
        ],
        scorer_name="structural-plus-hints",
    )

    assert scorer.__name__ == "structural-plus-hints"
    assert scorer(context) == 29.0

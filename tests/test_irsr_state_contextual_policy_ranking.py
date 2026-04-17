from pet.irsr_state import (
    advance_residual_state_once_with_ranked_policy_chain,
    collect_acceptable_residual_state_refinements,
    contextual_progress_score_by_structural_gain,
    contextual_progress_score_by_total_hint_delta,
    make_hostile_semiprime_residual_state,
    make_weighted_progress_scorer,
    rank_acceptable_residual_state_refinements,
    run_residual_state_frontier_until_quiescence_with_ranked_policy_chain,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_plain(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_a_with_hint(state: dict):
    refined = try_seed_residual_state_slot_candidates(state, "a", [101])
    if refined is None:
        return None
    refined["slots"][0]["pet_hints"]["near_generator"] = ["g1"]
    return refined


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_default_ranking_keeps_equal_structural_candidates_in_input_order():
    state = make_hostile_semiprime_residual_state(11413)

    ranked = rank_acceptable_residual_state_refinements(
        state,
        [_seed_a_plain, _seed_a_with_hint],
    )

    assert [item["refiner"] for item in ranked] == [
        "_seed_a_plain",
        "_seed_a_with_hint",
    ]


def test_contextual_ranking_can_prefer_hint_richer_refiner():
    state = make_hostile_semiprime_residual_state(11413)

    progress_scorer = make_weighted_progress_scorer(
        [
            (contextual_progress_score_by_structural_gain, 1.0),
            (contextual_progress_score_by_total_hint_delta, 10.0),
        ],
        scorer_name="prefer-hints-on-tie",
    )

    ranked = rank_acceptable_residual_state_refinements(
        state,
        [_seed_a_plain, _seed_a_with_hint],
        progress_scorer=progress_scorer,
    )

    assert [item["refiner"] for item in ranked] == [
        "_seed_a_with_hint",
        "_seed_a_plain",
    ]
    assert ranked[0]["score"] > ranked[1]["score"]


def test_ranked_policy_chain_can_use_contextual_progress_scorer():
    state = make_hostile_semiprime_residual_state(11413)

    progress_scorer = make_weighted_progress_scorer(
        [
            (contextual_progress_score_by_structural_gain, 1.0),
            (contextual_progress_score_by_total_hint_delta, 10.0),
        ],
        scorer_name="prefer-hints-on-tie",
    )

    result = advance_residual_state_once_with_ranked_policy_chain(
        state,
        open_refiners=[_seed_a_plain, _seed_a_with_hint],
        branch_refiners=[],
        progress_scorer=progress_scorer,
    )

    assert result["action"] == "refine"
    assert result["refiner"] == "_seed_a_with_hint"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["score"] > 11.0


def test_ranked_policy_runner_can_use_contextual_progress_scorer():
    state = make_hostile_semiprime_residual_state(11413)

    progress_scorer = make_weighted_progress_scorer(
        [
            (contextual_progress_score_by_structural_gain, 1.0),
            (contextual_progress_score_by_total_hint_delta, 10.0),
        ],
        scorer_name="prefer-hints-on-tie",
    )

    result = run_residual_state_frontier_until_quiescence_with_ranked_policy_chain(
        [state],
        5,
        open_refiners=[_seed_a_plain, _seed_a_with_hint, _seed_b_with_113],
        branch_refiners=[],
        progress_scorer=progress_scorer,
    )

    assert result["steps_run"] == 3
    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "_seed_a_with_hint"},
        {"step": 2, "action": "refine", "refiner": "_seed_b_with_113"},
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"

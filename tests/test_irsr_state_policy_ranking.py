from pet.irsr_state import (
    collect_acceptable_residual_state_refinements,
    make_hostile_semiprime_residual_state,
    rank_acceptable_residual_state_refinements,
    refine_residual_state_slot_candidates,
    select_best_residual_state_refinement,
    try_intersect_residual_state_slot_candidates,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _narrow_a_to_singleton(state: dict):
    return try_intersect_residual_state_slot_candidates(state, "a", [103])


def test_collect_acceptable_residual_state_refinements_keeps_only_acceptable_progress():
    state = make_hostile_semiprime_residual_state(11413)

    candidates = collect_acceptable_residual_state_refinements(
        state,
        [_seed_a_with_101, _seed_a_with_two],
    )

    assert [item["refiner"] for item in candidates] == [
        "_seed_a_with_101",
        "_seed_a_with_two",
    ]


def test_rank_acceptable_residual_state_refinements_orders_by_progress_score_desc():
    state = make_hostile_semiprime_residual_state(11413)

    ranked = rank_acceptable_residual_state_refinements(
        state,
        [_seed_a_with_two, _seed_a_with_101],
    )

    assert [item["refiner"] for item in ranked] == [
        "_seed_a_with_101",
        "_seed_a_with_two",
    ]
    assert ranked[0]["score"] > ranked[1]["score"]


def test_select_best_residual_state_refinement_picks_best_progress_not_first():
    state = make_hostile_semiprime_residual_state(11413)

    best = select_best_residual_state_refinement(
        state,
        [_seed_a_with_two, _seed_a_with_101],
    )

    assert best is not None
    assert best["refiner"] == "_seed_a_with_101"
    assert best["state"]["slots"][0]["domain"]["candidates"] == [101]


def test_select_best_residual_state_refinement_works_for_branchable_state():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    best = select_best_residual_state_refinement(
        state,
        [_narrow_a_to_singleton],
    )

    assert best is not None
    assert best["refiner"] == "_narrow_a_to_singleton"
    assert best["state"]["slots"][0]["domain"]["candidates"] == [103]

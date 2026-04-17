from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    run_residual_state_frontier_until_quiescence_with_ranked_policy_chain,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_ranked_policy_runner_refines_with_best_option_then_promotes():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_policy_chain(
        [state],
        5,
        open_refiners=[_seed_a_with_two, _seed_a_with_101, _seed_b_with_113],
        branch_refiners=[],
    )

    assert result["steps_run"] == 3
    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "_seed_a_with_101"},
        {"step": 2, "action": "refine", "refiner": "_seed_b_with_113"},
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"

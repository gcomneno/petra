from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    run_residual_state_frontier_until_quiescence_with_ranked_portfolios,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_ranked_portfolio_runner_traces_portfolio_origin_of_refinement():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        5,
        open_portfolios=[
            {"name": "broad-seeding", "refiners": [_seed_a_with_two]},
            {"name": "tight-seeding", "refiners": [_seed_a_with_101, _seed_b_with_113]},
        ],
        branch_portfolios=[],
    )

    assert result["steps_run"] == 3
    assert result["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "tight-seeding",
            "refiner": "_seed_a_with_101",
        },
        {
            "step": 2,
            "action": "refine",
            "portfolio": "tight-seeding",
            "refiner": "_seed_b_with_113",
        },
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"

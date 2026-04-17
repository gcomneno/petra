from pet.irsr_state import (
    advance_residual_state_once_with_ranked_portfolios,
    make_hostile_semiprime_residual_state,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def test_advance_residual_state_once_with_ranked_portfolios_reports_portfolio_and_refiner():
    state = make_hostile_semiprime_residual_state(11413)

    result = advance_residual_state_once_with_ranked_portfolios(
        state,
        open_portfolios=[
            {"name": "broad-seeding", "refiners": [_seed_a_with_two]},
            {"name": "tight-seeding", "refiners": [_seed_a_with_101]},
        ],
        branch_portfolios=[],
    )

    assert result["action"] == "refine"
    assert result["portfolio"] == "tight-seeding"
    assert result["refiner"] == "_seed_a_with_101"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["score"] > 0

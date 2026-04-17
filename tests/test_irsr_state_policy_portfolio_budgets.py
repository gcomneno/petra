from pet.irsr_state import (
    advance_residual_state_once_with_ranked_portfolios,
    make_hostile_semiprime_residual_state,
    run_residual_state_frontier_until_quiescence_with_ranked_portfolios,
    select_best_residual_state_refinement_from_portfolios,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_select_best_residual_state_refinement_from_portfolios_ignores_exhausted_portfolios():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "high-priority-tight", "priority": 100, "budget": 1, "refiners": [_seed_a_with_101]},
        {"name": "fallback-broad", "priority": 10, "budget": 1, "refiners": [_seed_a_with_two]},
    ]

    best = select_best_residual_state_refinement_from_portfolios(
        state,
        portfolios,
        portfolio_budget_state={
            "high-priority-tight": 0,
            "fallback-broad": 1,
        },
    )

    assert best is not None
    assert best["portfolio"] == "fallback-broad"
    assert best["refiner"] == "_seed_a_with_two"


def test_advance_residual_state_once_with_ranked_portfolios_reports_consumed_portfolio_budget():
    state = make_hostile_semiprime_residual_state(11413)

    result = advance_residual_state_once_with_ranked_portfolios(
        state,
        open_portfolios=[
            {"name": "tight-seeding", "priority": 100, "budget": 1, "refiners": [_seed_a_with_101]},
            {"name": "broad-seeding", "priority": 10, "budget": 1, "refiners": [_seed_a_with_two]},
        ],
        branch_portfolios=[],
        portfolio_budget_state={
            "tight-seeding": 1,
            "broad-seeding": 1,
        },
    )

    assert result["action"] == "refine"
    assert result["portfolio"] == "tight-seeding"
    assert result["refiner"] == "_seed_a_with_101"
    assert result["portfolio_budget_state"] == {
        "tight-seeding": 0,
        "broad-seeding": 1,
    }


def test_ranked_portfolio_runner_respects_budget_and_falls_back_to_next_portfolio():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        5,
        open_portfolios=[
            {"name": "tight-seeding", "priority": 100, "budget": 1, "refiners": [_seed_a_with_101]},
            {"name": "broad-seeding", "priority": 10, "budget": 2, "refiners": [_seed_b_with_113, _seed_a_with_two]},
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
            "portfolio": "broad-seeding",
            "refiner": "_seed_b_with_113",
        },
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"
    assert result["portfolio_budget_state"] == {
        "tight-seeding": 0,
        "broad-seeding": 1,
    }


def test_ranked_portfolio_runner_skips_zero_budget_portfolios_from_start():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        2,
        open_portfolios=[
            {"name": "blocked-tight", "priority": 100, "budget": 0, "refiners": [_seed_a_with_101]},
            {"name": "available-broad", "priority": 10, "budget": 1, "refiners": [_seed_a_with_two]},
        ],
        branch_portfolios=[],
    )

    assert result["steps_run"] == 2
    assert result["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "available-broad",
            "refiner": "_seed_a_with_two",
        },
        {
            "step": 2,
            "action": "branch",
            "slot": "a",
            "emitted": 2,
        },
    ]
    assert result["portfolio_budget_state"] == {
        "blocked-tight": 0,
        "available-broad": 0,
    }

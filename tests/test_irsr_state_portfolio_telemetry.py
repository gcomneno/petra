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


def test_ranked_portfolio_runner_reports_action_and_refiner_telemetry():
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
    assert result["telemetry"] == {
        "actions": {
            "refine": 2,
            "branch": 0,
            "promote": 1,
            "stop": 0,
            "idle": 0,
        },
        "portfolio_refine_counts": {
            "tight-seeding": 1,
            "broad-seeding": 1,
        },
        "refiner_refine_counts": {
            "_seed_a_with_101": 1,
            "_seed_b_with_113": 1,
        },
        "budget_consumed": {
            "tight-seeding": 1,
            "broad-seeding": 1,
        },
        "portfolio_family_refine_counts": {},
        "portfolio_family_budget_consumed": {},
    }


def test_ranked_portfolio_runner_reports_branch_and_idle_telemetry():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        2,
        open_portfolios=[
            {"name": "broad-seeding", "priority": 10, "budget": 1, "refiners": [_seed_a_with_two]},
        ],
        branch_portfolios=[],
    )

    assert result["steps_run"] == 2
    assert result["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "broad-seeding",
            "refiner": "_seed_a_with_two",
        },
        {
            "step": 2,
            "action": "branch",
            "slot": "a",
            "emitted": 2,
        },
    ]
    assert result["telemetry"] == {
        "actions": {
            "refine": 1,
            "branch": 1,
            "promote": 0,
            "stop": 0,
            "idle": 0,
        },
        "portfolio_refine_counts": {
            "broad-seeding": 1,
        },
        "refiner_refine_counts": {
            "_seed_a_with_two": 1,
        },
        "budget_consumed": {
            "broad-seeding": 1,
        },
        "portfolio_family_refine_counts": {},
        "portfolio_family_budget_consumed": {},
    }


def test_ranked_portfolio_runner_reports_idle_only_telemetry_when_nothing_progresses():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        1,
        open_portfolios=[],
        branch_portfolios=[],
    )

    assert result["steps_run"] == 1
    assert result["telemetry"] == {
        "actions": {
            "refine": 0,
            "branch": 0,
            "promote": 0,
            "stop": 0,
            "idle": 1,
        },
        "portfolio_refine_counts": {},
        "refiner_refine_counts": {},
        "budget_consumed": {},
        "portfolio_family_refine_counts": {},
        "portfolio_family_budget_consumed": {},
    }

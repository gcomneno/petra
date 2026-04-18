from pet.irsr_state import (
    advance_residual_state_once_with_ranked_portfolios,
    make_hostile_semiprime_residual_state,
    rank_acceptable_residual_state_refinements_from_portfolios,
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


def test_ranked_portfolios_order_by_priority_before_score():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "low-priority-tight", "priority": 10, "refiners": [_seed_a_with_101]},
        {"name": "high-priority-broad", "priority": 100, "refiners": [_seed_a_with_two]},
    ]

    ranked = rank_acceptable_residual_state_refinements_from_portfolios(
        state,
        portfolios,
    )

    assert [(item["portfolio"], item["refiner"]) for item in ranked] == [
        ("high-priority-broad", "_seed_a_with_two"),
        ("low-priority-tight", "_seed_a_with_101"),
    ]


def test_select_best_residual_state_refinement_from_portfolios_prefers_higher_priority_portfolio():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "low-priority-tight", "priority": 10, "refiners": [_seed_a_with_101]},
        {"name": "high-priority-broad", "priority": 100, "refiners": [_seed_a_with_two]},
    ]

    best = select_best_residual_state_refinement_from_portfolios(
        state,
        portfolios,
    )

    assert best is not None
    assert best["portfolio"] == "high-priority-broad"
    assert best["refiner"] == "_seed_a_with_two"
    assert best["state"]["slots"][0]["domain"]["candidates"] == [101, 103]


def test_select_best_residual_state_refinement_from_portfolios_uses_score_inside_same_priority():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {
            "name": "same-priority",
            "priority": 50,
            "refiners": [_seed_a_with_two, _seed_a_with_101],
        },
    ]

    best = select_best_residual_state_refinement_from_portfolios(
        state,
        portfolios,
    )

    assert best is not None
    assert best["portfolio"] == "same-priority"
    assert best["refiner"] == "_seed_a_with_101"
    assert best["state"]["slots"][0]["domain"]["candidates"] == [101]


def test_advance_residual_state_once_with_ranked_portfolios_reports_priority_selected_portfolio():
    state = make_hostile_semiprime_residual_state(11413)

    result = advance_residual_state_once_with_ranked_portfolios(
        state,
        open_portfolios=[
            {"name": "low-priority-tight", "priority": 10, "refiners": [_seed_a_with_101]},
            {"name": "high-priority-broad", "priority": 100, "refiners": [_seed_a_with_two]},
        ],
        branch_portfolios=[],
    )

    assert result["action"] == "refine"
    assert result["portfolio"] == "high-priority-broad"
    assert result["refiner"] == "_seed_a_with_two"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101, 103]


def test_ranked_portfolio_runner_traces_priority_driven_portfolio_choice():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_ranked_portfolios(
        [state],
        5,
        open_portfolios=[
            {"name": "low-priority-tight", "priority": 10, "refiners": [_seed_a_with_101]},
            {
                "name": "high-priority-broad",
                "priority": 100,
                "refiners": [_seed_a_with_two, _seed_b_with_113],
            },
        ],
        branch_portfolios=[],
    )

    assert result["steps_run"] == 3
    assert result["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "high-priority-broad",
            "refiner": "_seed_b_with_113",
        },
        {
            "step": 2,
            "action": "refine",
            "portfolio": "high-priority-broad",
            "refiner": "_seed_a_with_two",
        },
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"

from pet.irsr_state import (
    collect_acceptable_residual_state_refinements_from_portfolios,
    make_hostile_semiprime_residual_state,
    rank_acceptable_residual_state_refinements_from_portfolios,
    select_best_residual_state_refinement_from_portfolios,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_collect_acceptable_residual_state_refinements_from_portfolios_keeps_portfolio_name():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "open-seeding", "refiners": [_seed_a_with_two, _seed_a_with_101]},
        {"name": "secondary-seeding", "refiners": [_seed_b_with_113]},
    ]

    collected = collect_acceptable_residual_state_refinements_from_portfolios(
        state,
        portfolios,
    )

    assert [(item["portfolio"], item["refiner"]) for item in collected] == [
        ("open-seeding", "_seed_a_with_two"),
        ("open-seeding", "_seed_a_with_101"),
        ("secondary-seeding", "_seed_b_with_113"),
    ]


def test_rank_acceptable_residual_state_refinements_from_portfolios_orders_by_score():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "open-seeding", "refiners": [_seed_a_with_two, _seed_a_with_101]},
    ]

    ranked = rank_acceptable_residual_state_refinements_from_portfolios(
        state,
        portfolios,
    )

    assert [(item["portfolio"], item["refiner"]) for item in ranked] == [
        ("open-seeding", "_seed_a_with_101"),
        ("open-seeding", "_seed_a_with_two"),
    ]


def test_select_best_residual_state_refinement_from_portfolios_returns_best_candidate():
    state = make_hostile_semiprime_residual_state(11413)

    portfolios = [
        {"name": "open-seeding", "refiners": [_seed_a_with_two]},
        {"name": "priority-seeding", "refiners": [_seed_a_with_101]},
    ]

    best = select_best_residual_state_refinement_from_portfolios(
        state,
        portfolios,
    )

    assert best is not None
    assert best["portfolio"] == "priority-seeding"
    assert best["refiner"] == "_seed_a_with_101"
    assert best["state"]["slots"][0]["domain"]["candidates"] == [101]

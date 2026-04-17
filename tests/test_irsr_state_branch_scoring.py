from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    make_scored_branch_selector,
    refine_residual_state_slot_candidates,
    score_branchable_residual_state_slots,
    score_by_candidate_count,
    select_scored_branchable_slot,
)


def _make_state():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])
    return state


def test_score_branchable_residual_state_slots_reports_scores_in_state_order():
    state = _make_state()

    scored = score_branchable_residual_state_slots(state, score_by_candidate_count)

    assert scored == [
        {"slot": "a", "score": 3},
        {"slot": "b", "score": 2},
    ]


def test_select_scored_branchable_slot_can_minimize_score():
    state = _make_state()

    slot = select_scored_branchable_slot(
        state,
        score_by_candidate_count,
        maximize=False,
    )

    assert slot == "b"


def test_select_scored_branchable_slot_can_maximize_score():
    state = _make_state()

    slot = select_scored_branchable_slot(
        state,
        score_by_candidate_count,
        maximize=True,
    )

    assert slot == "a"


def test_select_scored_branchable_slot_uses_state_order_as_tie_break():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    slot = select_scored_branchable_slot(
        state,
        score_by_candidate_count,
        maximize=True,
    )

    assert slot == "a"


def test_make_scored_branch_selector_builds_callable_with_requested_name():
    selector = make_scored_branch_selector(
        score_by_candidate_count,
        maximize=False,
        selector_name="pick-smallest-domain",
    )

    assert selector.__name__ == "pick-smallest-domain"

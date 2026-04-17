from pet.irsr_state import (
    context_score_by_candidate_count,
    context_score_by_hint_density,
    make_contextual_branch_selector,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    select_contextual_branchable_slot,
)


def _make_state():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state["slots"][0]["pet_hints"]["near_generator"] = ["g1"]

    state = refine_residual_state_slot_candidates(state, "b", [113, 127])
    state["slots"][1]["pet_hints"]["near_generator"] = ["g1", "g2"]
    state["slots"][1]["pet_hints"]["block_shape"] = ["s1"]

    return state


def test_select_contextual_branchable_slot_can_minimize_candidate_count():
    state = _make_state()

    slot = select_contextual_branchable_slot(
        state,
        context_score_by_candidate_count,
        maximize=False,
    )

    assert slot == "b"


def test_select_contextual_branchable_slot_can_maximize_hint_density():
    state = _make_state()

    slot = select_contextual_branchable_slot(
        state,
        context_score_by_hint_density,
        maximize=True,
    )

    assert slot == "b"


def test_make_contextual_branch_selector_builds_named_callable():
    selector = make_contextual_branch_selector(
        context_score_by_hint_density,
        maximize=True,
        selector_name="prefer-hint-density",
    )

    assert selector.__name__ == "prefer-hint-density"

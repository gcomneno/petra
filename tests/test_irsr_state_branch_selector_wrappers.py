from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    select_max_width_branchable_slot,
    select_min_width_branchable_slot,
)


def test_width_selectors_keep_existing_behavior_after_scoring_generalization():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    assert select_min_width_branchable_slot(state) == "b"
    assert select_max_width_branchable_slot(state) == "a"

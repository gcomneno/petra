from pet.irsr_state import (
    branch_residual_state_with_selector,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    select_max_width_branchable_slot,
    select_min_width_branchable_slot,
)


def test_branch_residual_state_with_min_width_selector_branches_smallest_domain():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    branches = branch_residual_state_with_selector(state, select_min_width_branchable_slot)

    assert len(branches) == 2
    assert [branch["slots"][1]["domain"]["candidates"] for branch in branches] == [
        [113],
        [127],
    ]
    assert all(branch["slots"][0]["domain"]["candidates"] == [101, 103, 107] for branch in branches)


def test_branch_residual_state_with_max_width_selector_branches_largest_domain():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127, 131])

    branches = branch_residual_state_with_selector(state, select_max_width_branchable_slot)

    assert len(branches) == 3
    assert [branch["slots"][1]["domain"]["candidates"] for branch in branches] == [
        [113],
        [127],
        [131],
    ]
    assert all(branch["slots"][0]["domain"]["candidates"] == [101, 103] for branch in branches)

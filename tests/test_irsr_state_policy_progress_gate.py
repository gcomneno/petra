from copy import deepcopy

from pet.irsr_state import (
    advance_residual_state_once_with_policy_chain,
    advance_residual_state_once_with_prebranch_policy_chain,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    try_refine_branchable_residual_state_with_policy_chain,
    try_refine_open_residual_state_with_policy_chain,
    try_seed_residual_state_slot_candidates,
    try_intersect_residual_state_slot_candidates,
)


def _cosmetic_open_refiner(state: dict):
    updated = deepcopy(state)
    updated["slots"][0]["pet_hints"]["near_generator"].append("cosmetic")
    return updated


def _real_open_refiner(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _cosmetic_branch_refiner(state: dict):
    updated = deepcopy(state)
    updated["slots"][0]["pet_hints"]["block_shape"].append("cosmetic")
    return updated


def _real_branch_refiner(state: dict):
    return try_intersect_residual_state_slot_candidates(state, "a", [103])


def test_try_refine_open_residual_state_with_policy_chain_rejects_cosmetic_progress():
    state = make_hostile_semiprime_residual_state(11413)

    result = try_refine_open_residual_state_with_policy_chain(
        state,
        [_cosmetic_open_refiner],
    )

    assert result is None


def test_try_refine_open_residual_state_with_policy_chain_accepts_real_progress():
    state = make_hostile_semiprime_residual_state(11413)

    result = try_refine_open_residual_state_with_policy_chain(
        state,
        [_cosmetic_open_refiner, _real_open_refiner],
    )

    assert result is not None
    assert result["refiner"] == "_real_open_refiner"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["progress"]["empty_slot_count_delta"] == -1


def test_try_refine_branchable_residual_state_with_policy_chain_rejects_cosmetic_progress():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = try_refine_branchable_residual_state_with_policy_chain(
        state,
        [_cosmetic_branch_refiner],
    )

    assert result is None


def test_try_refine_branchable_residual_state_with_policy_chain_accepts_real_progress():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = try_refine_branchable_residual_state_with_policy_chain(
        state,
        [_cosmetic_branch_refiner, _real_branch_refiner],
    )

    assert result is not None
    assert result["refiner"] == "_real_branch_refiner"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [103]
    assert result["progress"]["candidate_count_delta"] == -1


def test_advance_residual_state_once_with_policy_chain_stays_idle_on_cosmetic_open_change():
    state = make_hostile_semiprime_residual_state(11413)

    result = advance_residual_state_once_with_policy_chain(
        state,
        [_cosmetic_open_refiner],
    )

    assert result == {
        "action": "idle",
        "reason": "open-without-branching-policy",
    }


def test_advance_residual_state_once_with_prebranch_policy_chain_still_branches_if_branch_refiner_is_only_cosmetic():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = advance_residual_state_once_with_prebranch_policy_chain(
        state,
        open_refiners=[],
        branch_refiners=[_cosmetic_branch_refiner],
    )

    assert result["action"] == "branch"
    assert result["slot"] == "a"

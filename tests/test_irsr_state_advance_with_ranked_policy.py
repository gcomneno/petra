from pet.irsr_state import (
    advance_residual_state_once_with_ranked_policy_chain,
    make_hostile_semiprime_residual_state,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def test_advance_residual_state_once_with_ranked_policy_chain_chooses_best_open_refiner():
    state = make_hostile_semiprime_residual_state(11413)

    result = advance_residual_state_once_with_ranked_policy_chain(
        state,
        open_refiners=[_seed_a_with_two, _seed_a_with_101],
        branch_refiners=[],
    )

    assert result["action"] == "refine"
    assert result["refiner"] == "_seed_a_with_101"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["score"] > 0

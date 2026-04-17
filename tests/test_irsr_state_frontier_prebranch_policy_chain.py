from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    make_intersect_first_branchable_slot_policy,
    make_seed_first_empty_slot_policy,
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain,
)


def test_prebranch_policy_chain_can_refine_before_branching_then_promote():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        5,
        open_refiners=[
            make_seed_first_empty_slot_policy([113], policy_name="seed-first-empty-113")
        ],
        branch_refiners=[
            make_intersect_first_branchable_slot_policy(
                [103], policy_name="narrow-first-branchable"
            )
        ],
    )

    assert result["steps_run"] == 3
    assert result["frontier"] == []
    assert result["frontier_summary"] == {
        "total": 0,
        "open": 0,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [103]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]
    assert result["stopped"] == []
    assert result["idle"] == []
    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "narrow-first-branchable"},
        {"step": 2, "action": "refine", "refiner": "seed-first-empty-113"},
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"


def test_prebranch_policy_chain_still_branches_when_no_branch_refiner_progresses():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        2,
        open_refiners=[],
        branch_refiners=[
            make_intersect_first_branchable_slot_policy(
                [101, 103], policy_name="no-op-branch-refiner"
            )
        ],
    )

    assert result["steps_run"] == 2
    assert len(result["frontier"]) == 2
    assert result["frontier_summary"] == {
        "total": 2,
        "open": 2,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["trace"] == [
        {"step": 1, "action": "branch", "emitted": 2},
        {"step": 2, "action": "idle"},
    ]
    assert result["termination_reason"] == "step-budget-exhausted"

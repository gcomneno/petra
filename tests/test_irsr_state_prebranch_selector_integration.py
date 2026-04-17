from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain,
    select_max_width_branchable_slot,
    select_min_width_branchable_slot,
)


def _make_three_slot_branchable_state():
    return {
        "target": {
            "n": "synthetic",
        },
        "skeleton": {
            "support_size": 3,
            "exponent_profile": [1, 1, 1],
            "squarefree": True,
            "normalized_order": "a<=b<=c",
        },
        "slots": [
            {
                "slot": "a",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [101, 103, 107],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
            {
                "slot": "b",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [113, 127],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
            {
                "slot": "c",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
        ],
        "coupling": {
            "product_constraint": "a*b*c=n",
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        },
        "refinement": {
            "iteration": 0,
            "status": "open",
            "payload_ready": False,
        },
    }


def test_prebranch_runner_promotes_payload_ready_state_before_any_selector_choice():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        1,
        open_refiners=[],
        branch_refiners=[],
        branch_selector=select_min_width_branchable_slot,
    )

    assert result["steps_run"] == 1
    assert result["trace"] == [
        {"step": 1, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"


def test_prebranch_runner_can_use_min_width_branch_selector_on_non_ready_state():
    state = _make_three_slot_branchable_state()

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        1,
        open_refiners=[],
        branch_refiners=[],
        branch_selector=select_min_width_branchable_slot,
    )

    assert result["steps_run"] == 1
    assert result["trace"] == [
        {"step": 1, "action": "branch", "slot": "b", "emitted": 2},
    ]
    assert result["termination_reason"] == "step-budget-exhausted"


def test_prebranch_runner_can_use_max_width_branch_selector_on_non_ready_state():
    state = _make_three_slot_branchable_state()

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        1,
        open_refiners=[],
        branch_refiners=[],
        branch_selector=select_max_width_branchable_slot,
    )

    assert result["steps_run"] == 1
    assert result["trace"] == [
        {"step": 1, "action": "branch", "slot": "a", "emitted": 3},
    ]
    assert result["termination_reason"] == "step-budget-exhausted"

from pet.irsr_state import (
    context_score_by_hint_density,
    make_contextual_branch_selector,
    run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain,
)


def _make_three_slot_branchable_state():
    return {
        "target": {"n": "synthetic"},
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
                    "near_generator": ["g1"],
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
                    "near_generator": ["g1", "g2"],
                    "block_shape": ["s1"],
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


def test_prebranch_runner_can_use_contextual_branch_selector():
    state = _make_three_slot_branchable_state()

    selector = make_contextual_branch_selector(
        context_score_by_hint_density,
        maximize=True,
        selector_name="prefer-hint-density",
    )

    result = run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain(
        [state],
        1,
        open_refiners=[],
        branch_refiners=[],
        branch_selector=selector,
    )

    assert result["steps_run"] == 1
    assert result["trace"] == [
        {"step": 1, "action": "branch", "slot": "b", "emitted": 2},
    ]
    assert result["termination_reason"] == "step-budget-exhausted"

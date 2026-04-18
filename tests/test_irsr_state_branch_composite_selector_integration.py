from pet.irsr_state import (
    make_weighted_branch_selector,
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence_with_prebranch_policy_chain,
    score_by_candidate_count,
    score_by_total_hint_count,
)


def _make_state():
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


def test_prebranch_runner_can_use_weighted_branch_selector():
    state = _make_state()

    selector = make_weighted_branch_selector(
        [
            (score_by_candidate_count, -1),
            (score_by_total_hint_count, 10),
        ],
        maximize=True,
        selector_name="prefer-hints",
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

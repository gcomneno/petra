from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    make_seed_first_empty_slot_policy,
    make_seed_slot_policy,
    run_residual_state_frontier_until_quiescence_with_policy_chain,
)


def test_policy_chain_can_fill_slots_without_hardcoding_helper_functions():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_policy_chain(
        [state],
        5,
        [
            make_seed_slot_policy("a", [101], policy_name="seed-a-101"),
            make_seed_slot_policy("b", [113], policy_name="seed-b-113"),
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
    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "seed-a-101"},
        {"step": 2, "action": "refine", "refiner": "seed-b-113"},
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]


def test_first_empty_slot_policy_reapplies_first_matching_refiner_in_chain_order():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_policy_chain(
        [state],
        5,
        [
            make_seed_first_empty_slot_policy([101], policy_name="seed-first-empty-101"),
            make_seed_first_empty_slot_policy([113], policy_name="seed-first-empty-113"),
        ],
    )

    assert result["steps_run"] == 3
    assert result["frontier"] == []
    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "seed-first-empty-101"},
        {"step": 2, "action": "refine", "refiner": "seed-first-empty-101"},
        {"step": 3, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101]},
                {"slot": "b", "candidates": [101]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]


def test_slot_specific_seed_policies_are_the_right_tool_for_distinct_slot_values():
    state = make_hostile_semiprime_residual_state(11413)

    result = run_residual_state_frontier_until_quiescence_with_policy_chain(
        [state],
        5,
        [
            make_seed_slot_policy("a", [101], policy_name="seed-a-101"),
            make_seed_slot_policy("b", [113], policy_name="seed-b-113"),
        ],
    )

    assert result["trace"] == [
        {"step": 1, "action": "refine", "refiner": "seed-a-101"},
        {"step": 2, "action": "refine", "refiner": "seed-b-113"},
        {"step": 3, "action": "promote"},
    ]

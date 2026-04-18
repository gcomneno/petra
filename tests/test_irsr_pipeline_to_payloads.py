from pet.irsr_state import (
    extract_builder_payload_candidates_from_irsr_run,
    run_hostile_semiprime_irsr_to_payload_candidates,
    summarize_irsr_payload_candidates,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_extract_builder_payload_candidates_from_irsr_run_returns_promoted_payloads():
    run_result = {
        "promoted": [
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
    }

    assert extract_builder_payload_candidates_from_irsr_run(run_result) == run_result["promoted"]


def test_summarize_irsr_payload_candidates_reports_empty_result():
    assert summarize_irsr_payload_candidates([]) == {
        "payload_count": 0,
        "support_sizes": [],
        "exponent_profiles": [],
    }


def test_summarize_irsr_payload_candidates_reports_basic_shape_summary():
    payloads = [
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

    assert summarize_irsr_payload_candidates(payloads) == {
        "payload_count": 1,
        "support_sizes": [2],
        "exponent_profiles": [[1, 1]],
    }


def test_run_hostile_semiprime_irsr_to_payload_candidates_emits_builder_ready_payload():
    result = run_hostile_semiprime_irsr_to_payload_candidates(
        11413,
        max_steps=5,
        open_portfolios=[
            {"name": "tight-seeding", "priority": 100, "budget": 2, "refiners": [_seed_a_with_101, _seed_b_with_113]},
        ],
        branch_portfolios=[],
    )

    assert result["input"] == {
        "n": "11413",
        "kind": "hostile-semiprime",
    }
    assert result["payload_candidates"] == [
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
    assert result["payload_summary"] == {
        "payload_count": 1,
        "support_sizes": [2],
        "exponent_profiles": [[1, 1]],
    }
    assert result["run"]["termination_reason"] == "frontier-exhausted"
    assert result["run"]["steps_run"] == 3


def test_run_hostile_semiprime_irsr_to_payload_candidates_reports_empty_payloads_when_no_progress():
    result = run_hostile_semiprime_irsr_to_payload_candidates(
        11413,
        max_steps=1,
        open_portfolios=[],
        branch_portfolios=[],
    )

    assert result["payload_candidates"] == []
    assert result["payload_summary"] == {
        "payload_count": 0,
        "support_sizes": [],
        "exponent_profiles": [],
    }
    assert result["run"]["termination_reason"] == "step-budget-exhausted"

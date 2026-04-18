from pet.irsr_state import (
    classify_irsr_builder_outcome,
    run_hostile_semiprime_irsr_to_builder_results,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_classify_irsr_builder_outcome_reports_no_payload_candidates():
    result = {
        "payload_candidates": [],
        "build_results": [],
    }

    assert classify_irsr_builder_outcome(result) == "no-payload-candidates"


def test_classify_irsr_builder_outcome_reports_payloads_nonexact():
    result = {
        "payload_candidates": [
            {
                "support_size": 2,
                "exponent_profile": [1, 1],
                "prime_slots": [
                    {"slot": "a", "candidates": [101, 103]},
                    {"slot": "b", "candidates": [113]},
                ],
                "joint_pet_constraints": [],
                "forbidden_patterns": [],
            }
        ],
        "build_results": [
            {
                "build_attempted": False,
                "skip_reason": "non-exact-payload-candidates",
                "factorization_spec": None,
            }
        ],
    }

    assert classify_irsr_builder_outcome(result) == "payloads-nonexact"


def test_classify_irsr_builder_outcome_reports_builder_attempted_no_build():
    result = {
        "payload_candidates": [{"dummy": True}],
        "build_results": [
            {
                "build_attempted": True,
                "report": {
                    "support_report": {"exact_target_match": False},
                    "final_build_output": {"build_status": "deferred"},
                },
            }
        ],
    }

    assert classify_irsr_builder_outcome(result) == "builder-attempted-no-build"


def test_classify_irsr_builder_outcome_reports_built():
    result = {
        "payload_candidates": [{"dummy": True}],
        "build_results": [
            {
                "build_attempted": True,
                "report": {
                    "support_report": {"exact_target_match": False},
                    "final_build_output": {"build_status": "built"},
                },
            }
        ],
    }

    assert classify_irsr_builder_outcome(result) == "built"


def test_classify_irsr_builder_outcome_reports_built_exact_match():
    result = {
        "payload_candidates": [{"dummy": True}],
        "build_results": [
            {
                "build_attempted": True,
                "report": {
                    "support_report": {"exact_target_match": True},
                    "final_build_output": {"build_status": "built"},
                },
            }
        ],
    }

    assert classify_irsr_builder_outcome(result) == "built-exact-match"


def test_run_hostile_semiprime_irsr_to_builder_results_reports_no_payload_candidates_status(tmp_path):
    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=1,
        open_portfolios=[],
        branch_portfolios=[],
        output_dir=tmp_path / "artifacts",
    )

    assert result["final_status"] == "no-payload-candidates"


def test_run_hostile_semiprime_irsr_to_builder_results_reports_payloads_nonexact_status(tmp_path):
    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=3,
        open_portfolios=[
            {
                "name": "broad-seeding",
                "priority": 100,
                "budget": 2,
                "refiners": [_seed_a_with_two, _seed_b_with_113],
            }
        ],
        branch_portfolios=[],
        output_dir=tmp_path / "artifacts",
    )

    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"


def test_run_hostile_semiprime_irsr_to_builder_results_reports_built_exact_match_status(tmp_path):
    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=5,
        open_portfolios=[
            {
                "name": "tight-seeding",
                "priority": 100,
                "budget": 2,
                "refiners": [_seed_a_with_101, _seed_b_with_113],
            }
        ],
        branch_portfolios=[],
        output_dir=tmp_path / "artifacts",
    )

    assert result["build_summary"]["built_count"] == 1
    assert result["build_summary"]["exact_match_count"] == 1
    assert result["final_status"] == "built-exact-match"

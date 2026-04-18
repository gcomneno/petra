from pathlib import Path
from pet.irsr_state import (
    irsr_payload_candidate_to_factorization_spec,
    run_builder_on_irsr_payload_candidate,
    run_hostile_semiprime_irsr_to_builder_results,
    summarize_irsr_builder_results,
    try_seed_residual_state_slot_candidates,
)


def _exact_payload():
    return {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "prime_slots": [
            {"slot": "a", "candidates": [101]},
            {"slot": "b", "candidates": [113]},
        ],
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }


def _nonexact_payload():
    return {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "prime_slots": [
            {"slot": "a", "candidates": [101, 103]},
            {"slot": "b", "candidates": [113]},
        ],
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_irsr_payload_candidate_to_factorization_spec_returns_exact_factorization():
    assert irsr_payload_candidate_to_factorization_spec(_exact_payload()) == {
        "factors": [[101, 1], [113, 1]],
    }


def test_irsr_payload_candidate_to_factorization_spec_returns_none_for_nonexact_payload():
    assert irsr_payload_candidate_to_factorization_spec(_nonexact_payload()) is None


def test_run_builder_on_irsr_payload_candidate_builds_exact_payload(tmp_path: Path):
    result = run_builder_on_irsr_payload_candidate(
        _exact_payload(),
        tmp_path / "artifacts",
    )

    assert result["build_attempted"] is True
    assert result["factorization_spec"] == {
        "factors": [[101, 1], [113, 1]],
    }
    assert result["report"]["schema"] == "pet-builder-from-factorization-v0"
    assert result["report"]["final_build_output"]["build_status"] == "built"
    assert result["report"]["support_report"]["exact_target_match"] is True


def test_run_builder_on_irsr_payload_candidate_skips_nonexact_payload(tmp_path: Path):
    result = run_builder_on_irsr_payload_candidate(
        _nonexact_payload(),
        tmp_path / "artifacts",
    )

    assert result == {
        "build_attempted": False,
        "skip_reason": "non-exact-payload-candidates",
        "factorization_spec": None,
    }


def test_summarize_irsr_builder_results_reports_empty_summary():
    assert summarize_irsr_builder_results([]) == {
        "candidate_count": 0,
        "attempted_count": 0,
        "built_count": 0,
        "exact_match_count": 0,
        "skipped_count": 0,
    }


def test_summarize_irsr_builder_results_reports_attempted_and_skipped_cases():
    summary = summarize_irsr_builder_results(
        [
            {
                "build_attempted": True,
                "report": {
                    "support_report": {"exact_target_match": True},
                    "final_build_output": {"build_status": "built"},
                },
            },
            {
                "build_attempted": False,
                "skip_reason": "non-exact-payload-candidates",
                "factorization_spec": None,
            },
        ]
    )

    assert summary == {
        "candidate_count": 2,
        "attempted_count": 1,
        "built_count": 1,
        "exact_match_count": 1,
        "skipped_count": 1,
    }


def test_run_hostile_semiprime_irsr_to_builder_results_builds_exact_promoted_payload(tmp_path: Path):
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

    assert result["input"] == {
        "n": "11413",
        "kind": "hostile-semiprime",
    }
    assert result["payload_summary"] == {
        "payload_count": 1,
        "support_sizes": [2],
        "exponent_profiles": [[1, 1]],
    }
    assert len(result["build_results"]) == 1
    assert result["build_results"][0]["build_attempted"] is True
    assert result["build_results"][0]["report"]["final_build_output"]["build_status"] == "built"
    assert result["build_summary"] == {
        "candidate_count": 1,
        "attempted_count": 1,
        "built_count": 1,
        "exact_match_count": 1,
        "skipped_count": 0,
    }


def test_run_hostile_semiprime_irsr_to_builder_results_reports_no_builds_when_no_payloads(tmp_path: Path):
    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=1,
        open_portfolios=[],
        branch_portfolios=[],
        output_dir=tmp_path / "artifacts",
    )

    assert result["payload_candidates"] == []
    assert result["build_results"] == []
    assert result["build_summary"] == {
        "candidate_count": 0,
        "attempted_count": 0,
        "built_count": 0,
        "exact_match_count": 0,
        "skipped_count": 0,
    }

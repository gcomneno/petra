from pet.irsr_state import (
    compare_hostile_semiprime_auto_seed_runs,
    score_irsr_final_status,
    select_best_hostile_semiprime_auto_seed_run,
)


def test_score_irsr_final_status_orders_outcomes_by_operational_value():
    assert score_irsr_final_status("no-payload-candidates") == 0
    assert score_irsr_final_status("payloads-nonexact") == 1
    assert score_irsr_final_status("builder-attempted-no-build") == 2
    assert score_irsr_final_status("built") == 3
    assert score_irsr_final_status("built-exact-match") == 4


def test_select_best_hostile_semiprime_auto_seed_run_prefers_higher_final_status():
    runs = [
        {
            "name": "sqrt-auto-wide",
            "sqrt_radii": [4],
            "final_status": "payloads-nonexact",
            "payload_summary": {"payload_count": 1},
            "build_summary": {"built_count": 0, "exact_match_count": 0},
        },
        {
            "name": "sqrt-auto-tight",
            "sqrt_radii": [1],
            "final_status": "built-exact-match",
            "payload_summary": {"payload_count": 1},
            "build_summary": {"built_count": 1, "exact_match_count": 1},
        },
    ]

    best = select_best_hostile_semiprime_auto_seed_run(runs)

    assert best["name"] == "sqrt-auto-tight"
    assert best["final_status"] == "built-exact-match"


def test_compare_hostile_semiprime_auto_seed_runs_reports_best_run_for_easy_case(tmp_path):
    result = compare_hostile_semiprime_auto_seed_runs(
        10403,
        auto_seed_specs=[
            {
                "name": "sqrt-auto-r1",
                "sqrt_radii": [1],
            },
            {
                "name": "sqrt-auto-r4",
                "sqrt_radii": [4],
            },
        ],
        max_steps=5,
        output_dir=tmp_path / "artifacts",
    )

    assert result["input"] == {
        "n": "10403",
        "kind": "hostile-semiprime",
    }
    assert [run["name"] for run in result["runs"]] == [
        "sqrt-auto-r1",
        "sqrt-auto-r4",
    ]
    assert result["best_run"]["name"] == "sqrt-auto-r1"
    assert result["best_run"]["final_status"] == "built-exact-match"


def test_compare_hostile_semiprime_auto_seed_runs_reports_payload_only_outcome_for_11413(tmp_path):
    result = compare_hostile_semiprime_auto_seed_runs(
        11413,
        auto_seed_specs=[
            {
                "name": "sqrt-auto-r1",
                "sqrt_radii": [1],
            },
            {
                "name": "sqrt-auto-r2-r4",
                "sqrt_radii": [2, 4],
            },
        ],
        max_steps=5,
        output_dir=tmp_path / "artifacts",
    )

    assert result["input"] == {
        "n": "11413",
        "kind": "hostile-semiprime",
    }
    assert [run["final_status"] for run in result["runs"]] == [
        "no-payload-candidates",
        "payloads-nonexact",
    ]
    assert result["best_run"]["final_status"] == "payloads-nonexact"

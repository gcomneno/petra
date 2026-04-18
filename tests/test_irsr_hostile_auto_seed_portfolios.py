from pet.irsr_state import (
    build_hostile_semiprime_auto_seed_portfolios,
    run_hostile_semiprime_irsr_with_auto_seed_portfolios,
)


def test_build_hostile_semiprime_auto_seed_portfolios_builds_sqrt_ladder_from_n():
    portfolios = build_hostile_semiprime_auto_seed_portfolios(
        11413,
        sqrt_radii=[1, 2, 4],
        base_priority=100,
        priority_step=10,
        budget=1,
    )

    assert [portfolio["name"] for portfolio in portfolios] == [
        "sqrt-auto-r1",
        "sqrt-auto-r2",
        "sqrt-auto-r4",
    ]
    assert [portfolio["family"] for portfolio in portfolios] == [
        "sqrt-auto",
        "sqrt-auto",
        "sqrt-auto",
    ]
    assert [portfolio["priority"] for portfolio in portfolios] == [100, 90, 80]
    assert [portfolio["budget"] for portfolio in portfolios] == [1, 1, 1]
    assert [len(portfolio["refiners"]) for portfolio in portfolios] == [2, 2, 2]


def test_run_hostile_semiprime_irsr_with_auto_seed_portfolios_can_build_easy_balanced_case(tmp_path):
    result = run_hostile_semiprime_irsr_with_auto_seed_portfolios(
        10403,
        sqrt_radii=[1, 2, 4],
        max_steps=5,
        output_dir=tmp_path / "artifacts",
    )

    assert result["input"] == {
        "n": "10403",
        "kind": "hostile-semiprime",
    }
    assert result["payload_summary"] == {
        "payload_count": 1,
        "support_sizes": [2],
        "exponent_profiles": [[1, 1]],
    }
    assert result["build_summary"]["built_count"] == 1
    assert result["final_status"] == "built-exact-match"


def test_run_hostile_semiprime_irsr_with_auto_seed_portfolios_reports_nonexact_status_for_11413(tmp_path):
    result = run_hostile_semiprime_irsr_with_auto_seed_portfolios(
        11413,
        sqrt_radii=[1, 2, 4],
        max_steps=5,
        output_dir=tmp_path / "artifacts",
    )

    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"


def test_run_hostile_semiprime_irsr_with_auto_seed_portfolios_reports_sqrt_auto_family_telemetry(tmp_path):
    result = run_hostile_semiprime_irsr_with_auto_seed_portfolios(
        10403,
        sqrt_radii=[1, 2, 4],
        max_steps=5,
        output_dir=tmp_path / "artifacts",
    )

    assert result["run"]["telemetry"]["portfolio_family_refine_counts"] == {
        "sqrt-auto": 2,
    }
    assert result["run"]["telemetry"]["portfolio_family_budget_consumed"] == {
        "sqrt-auto": 2,
    }

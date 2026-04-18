from pet.irsr_state import (
    build_hostile_semiprime_seed_portfolios,
    run_hostile_semiprime_irsr_with_multi_seed_portfolios,
)


def test_build_hostile_semiprime_seed_portfolios_tags_seed_family_on_each_portfolio():
    portfolios = build_hostile_semiprime_seed_portfolios(
        11413,
        candidate_seed_specs=[
            {
                "slot_candidates": {
                    "a": [101],
                    "b": [113],
                },
                "name": "candidate-baseline",
                "priority": 100,
                "budget": 1,
            }
        ],
        range_seed_specs=[
            {
                "slot_ranges": {
                    "a": {"min": 100, "max": 104},
                    "b": {"min": 113, "max": 113},
                },
                "name": "range-baseline",
                "priority": 80,
                "budget": 1,
            }
        ],
        sqrt_seed_specs=[
            {
                "radius": 6,
                "name": "sqrt-baseline",
                "priority": 60,
                "budget": 1,
            }
        ],
    )

    assert [(p["name"], p["family"]) for p in portfolios] == [
        ("candidate-baseline", "candidate"),
        ("range-baseline", "range"),
        ("sqrt-baseline", "sqrt"),
    ]


def test_multi_seed_runner_reports_family_telemetry_for_candidate_wins(tmp_path):
    result = run_hostile_semiprime_irsr_with_multi_seed_portfolios(
        11413,
        max_steps=5,
        candidate_seed_specs=[
            {
                "slot_candidates": {
                    "a": [101],
                    "b": [113],
                },
                "name": "candidate-baseline",
                "priority": 100,
                "budget": 2,
            }
        ],
        sqrt_seed_specs=[
            {
                "radius": 6,
                "name": "sqrt-baseline",
                "priority": 60,
                "budget": 1,
            }
        ],
        output_dir=tmp_path / "artifacts",
    )

    assert result["final_status"] == "built-exact-match"
    assert result["run"]["telemetry"]["portfolio_family_refine_counts"] == {
        "candidate": 2,
    }
    assert result["run"]["telemetry"]["portfolio_family_budget_consumed"] == {
        "candidate": 2,
    }


def test_multi_seed_runner_reports_family_telemetry_for_range_fallback(tmp_path):
    result = run_hostile_semiprime_irsr_with_multi_seed_portfolios(
        11413,
        max_steps=5,
        candidate_seed_specs=[],
        range_seed_specs=[
            {
                "slot_ranges": {
                    "a": {"min": 100, "max": 104},
                    "b": {"min": 113, "max": 113},
                },
                "name": "range-baseline",
                "priority": 80,
                "budget": 2,
            }
        ],
        sqrt_seed_specs=[],
        output_dir=tmp_path / "artifacts",
    )

    assert result["final_status"] == "payloads-nonexact"
    assert result["run"]["telemetry"]["portfolio_family_refine_counts"] == {
        "range": 2,
    }
    assert result["run"]["telemetry"]["portfolio_family_budget_consumed"] == {
        "range": 2,
    }


def test_multi_seed_runner_reports_family_telemetry_for_sqrt_only_run(tmp_path):
    result = run_hostile_semiprime_irsr_with_multi_seed_portfolios(
        10403,
        max_steps=5,
        candidate_seed_specs=[],
        range_seed_specs=[],
        sqrt_seed_specs=[
            {
                "radius": 1,
                "name": "sqrt-baseline",
                "priority": 60,
                "budget": 2,
            }
        ],
        output_dir=tmp_path / "artifacts",
    )

    assert result["final_status"] == "built-exact-match"
    assert result["run"]["telemetry"]["portfolio_family_refine_counts"] == {
        "sqrt": 2,
    }
    assert result["run"]["telemetry"]["portfolio_family_budget_consumed"] == {
        "sqrt": 2,
    }

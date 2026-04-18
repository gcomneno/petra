from pet.irsr_state import (
    derive_hostile_semiprime_sqrt_slot_ranges,
    make_hostile_semiprime_sqrt_seed_portfolio,
    run_hostile_semiprime_irsr_with_sqrt_seed_baseline,
)


def test_derive_hostile_semiprime_sqrt_slot_ranges_splits_window_around_isqrt():
    assert derive_hostile_semiprime_sqrt_slot_ranges(11413, radius=6) == {
        "a": {"min": 100, "max": 106},
        "b": {"min": 107, "max": 113},
    }


def test_make_hostile_semiprime_sqrt_seed_portfolio_builds_named_budgeted_portfolio():
    portfolio = make_hostile_semiprime_sqrt_seed_portfolio(
        11413,
        radius=6,
        name="hostile-semiprime-sqrt-baseline",
        priority=60,
        budget=2,
    )

    assert portfolio["name"] == "hostile-semiprime-sqrt-baseline"
    assert portfolio["priority"] == 60
    assert portfolio["budget"] == 2
    assert len(portfolio["refiners"]) == 2
    assert [refiner.__name__ for refiner in portfolio["refiners"]] == [
        "seed_a_range",
        "seed_b_range",
    ]


def test_run_hostile_semiprime_irsr_with_sqrt_seed_baseline_reports_payloads_nonexact_for_11413():
    result = run_hostile_semiprime_irsr_with_sqrt_seed_baseline(
        11413,
        radius=6,
        max_steps=5,
    )

    assert result["input"] == {
        "n": "11413",
        "kind": "hostile-semiprime",
    }
    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"


def test_run_hostile_semiprime_irsr_with_sqrt_seed_baseline_can_build_easy_balanced_case():
    result = run_hostile_semiprime_irsr_with_sqrt_seed_baseline(
        10403,
        radius=1,
        max_steps=5,
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
    assert result["build_summary"]["exact_match_count"] == 1
    assert result["final_status"] == "built-exact-match"

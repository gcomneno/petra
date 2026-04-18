from pet.irsr_state import (
    build_hostile_semiprime_seed_portfolios,
    run_hostile_semiprime_irsr_with_multi_seed_portfolios,
)


def test_build_hostile_semiprime_seed_portfolios_can_mix_candidate_range_and_sqrt_sources():
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

    assert [portfolio["name"] for portfolio in portfolios] == [
        "candidate-baseline",
        "range-baseline",
        "sqrt-baseline",
    ]
    assert [portfolio["priority"] for portfolio in portfolios] == [100, 80, 60]
    assert [portfolio["budget"] for portfolio in portfolios] == [1, 1, 1]
    assert [len(portfolio["refiners"]) for portfolio in portfolios] == [2, 2, 2]


def test_run_hostile_semiprime_irsr_with_multi_seed_portfolios_prefers_higher_priority_seed_source(tmp_path):
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

    assert result["input"] == {
        "n": "11413",
        "kind": "hostile-semiprime",
    }
    assert result["final_status"] == "built-exact-match"
    assert result["build_summary"]["built_count"] == 1
    assert result["run"]["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "candidate-baseline",
            "refiner": "seed_a_candidates",
        },
        {
            "step": 2,
            "action": "refine",
            "portfolio": "candidate-baseline",
            "refiner": "seed_b_candidates",
        },
        {"step": 3, "action": "promote"},
    ]


def test_run_hostile_semiprime_irsr_with_multi_seed_portfolios_can_fall_back_to_range_seed(tmp_path):
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

    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"
    assert result["run"]["trace"] == [
        {
            "step": 1,
            "action": "refine",
            "portfolio": "range-baseline",
            "refiner": "seed_b_range",
        },
        {
            "step": 2,
            "action": "refine",
            "portfolio": "range-baseline",
            "refiner": "seed_a_range",
        },
        {"step": 3, "action": "promote"},
    ]


def test_run_hostile_semiprime_irsr_with_multi_seed_portfolios_can_use_sqrt_baseline_alone(tmp_path):
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

    assert result["payload_summary"] == {
        "payload_count": 1,
        "support_sizes": [2],
        "exponent_profiles": [[1, 1]],
    }
    assert result["build_summary"]["built_count"] == 1
    assert result["final_status"] == "built-exact-match"

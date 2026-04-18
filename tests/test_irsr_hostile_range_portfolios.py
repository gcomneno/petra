from pet.irsr_state import (
    make_hostile_semiprime_range_seed_portfolio,
    make_slot_prime_range_seed_refiner,
    primes_in_closed_range,
    run_hostile_semiprime_irsr_with_seed_ranges,
)


def test_primes_in_closed_range_returns_primes_only():
    assert primes_in_closed_range(100, 110) == [101, 103, 107, 109]


def test_make_slot_prime_range_seed_refiner_materializes_prime_candidates_from_range():
    refiner = make_slot_prime_range_seed_refiner(
        "a",
        100,
        110,
        policy_name="seed-a-range",
    )

    state = {
        "target": {"n": "11413"},
        "skeleton": {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "squarefree": True,
            "normalized_order": "a<=b",
        },
        "slots": [
            {
                "slot": "a",
                "kind": "prime",
                "domain": {"type": "range_or_candidates", "min": None, "max": None, "candidates": []},
                "pet_hints": {"near_generator": [], "block_shape": []},
            },
            {
                "slot": "b",
                "kind": "prime",
                "domain": {"type": "range_or_candidates", "min": None, "max": None, "candidates": []},
                "pet_hints": {"near_generator": [], "block_shape": []},
            },
        ],
        "coupling": {
            "product_constraint": "a*b=n",
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        },
        "refinement": {
            "iteration": 0,
            "status": "open",
            "payload_ready": False,
        },
    }

    refined = refiner(state)

    assert refiner.__name__ == "seed-a-range"
    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [101, 103, 107, 109]
    assert refined["slots"][1]["domain"]["candidates"] == []


def test_make_hostile_semiprime_range_seed_portfolio_builds_named_budgeted_portfolio():
    portfolio = make_hostile_semiprime_range_seed_portfolio(
        {
            "a": {"min": 100, "max": 110},
            "b": {"min": 113, "max": 113},
        },
        name="hostile-semiprime-range-baseline",
        priority=70,
        budget=2,
    )

    assert portfolio["name"] == "hostile-semiprime-range-baseline"
    assert portfolio["priority"] == 70
    assert portfolio["budget"] == 2
    assert len(portfolio["refiners"]) == 2
    assert [refiner.__name__ for refiner in portfolio["refiners"]] == [
        "seed_a_range",
        "seed_b_range",
    ]


def test_run_hostile_semiprime_irsr_with_seed_ranges_builds_exact_match_for_tight_windows():
    result = run_hostile_semiprime_irsr_with_seed_ranges(
        11413,
        {
            "a": {"min": 101, "max": 101},
            "b": {"min": 113, "max": 113},
        },
        max_steps=5,
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
    assert result["build_summary"]["built_count"] == 1
    assert result["final_status"] == "built-exact-match"


def test_run_hostile_semiprime_irsr_with_seed_ranges_reports_payloads_nonexact_for_ambiguous_window():
    result = run_hostile_semiprime_irsr_with_seed_ranges(
        11413,
        {
            "a": {"min": 100, "max": 104},
            "b": {"min": 113, "max": 113},
        },
        max_steps=5,
    )

    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"

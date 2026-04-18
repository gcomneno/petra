from pet.irsr_state import (
    make_hostile_semiprime_seed_portfolio,
    make_slot_candidate_seed_refiner,
    run_hostile_semiprime_irsr_with_seed_candidates,
)


def test_make_slot_candidate_seed_refiner_seeds_requested_slot():
    refiner = make_slot_candidate_seed_refiner(
        "a",
        [101, 103],
        policy_name="seed-a-candidates",
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

    assert refiner.__name__ == "seed-a-candidates"
    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [101, 103]
    assert refined["slots"][1]["domain"]["candidates"] == []


def test_make_hostile_semiprime_seed_portfolio_builds_named_budgeted_portfolio():
    portfolio = make_hostile_semiprime_seed_portfolio(
        {
            "a": [101, 103],
            "b": [113],
        },
        name="hostile-semiprime-baseline",
        priority=80,
        budget=2,
    )

    assert portfolio["name"] == "hostile-semiprime-baseline"
    assert portfolio["priority"] == 80
    assert portfolio["budget"] == 2
    assert len(portfolio["refiners"]) == 2
    assert [refiner.__name__ for refiner in portfolio["refiners"]] == [
        "seed_a_candidates",
        "seed_b_candidates",
    ]


def test_run_hostile_semiprime_irsr_with_seed_candidates_builds_promoted_payload():
    result = run_hostile_semiprime_irsr_with_seed_candidates(
        11413,
        {
            "a": [101],
            "b": [113],
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
    assert result["final_status"] == "built-exact-match"
    assert result["build_summary"]["built_count"] == 1
    assert result["run"]["termination_reason"] == "frontier-exhausted"


def test_run_hostile_semiprime_irsr_with_seed_candidates_reports_payloads_nonexact_for_ambiguous_slot():
    result = run_hostile_semiprime_irsr_with_seed_candidates(
        11413,
        {
            "a": [101, 103],
            "b": [113],
        },
        max_steps=5,
    )

    assert result["payload_candidates"] != []
    assert result["build_summary"]["attempted_count"] == 0
    assert result["final_status"] == "payloads-nonexact"

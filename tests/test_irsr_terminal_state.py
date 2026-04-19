from pet.irsr_state import (
    run_hostile_semiprime_irsr_to_builder_results,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_two(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101, 103])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def test_terminal_state_reports_blocked_when_no_payload_candidates(tmp_path):
    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=1,
        open_portfolios=[],
        branch_portfolios=[],
        output_dir=tmp_path / "artifacts",
    )

    terminal = result["terminal_state"]
    assert terminal["status"] == "blocked"
    assert terminal["reason"] == "no-payload-candidates"
    assert terminal["input"] == {"n": "11413", "kind": "hostile-semiprime"}
    assert terminal["builder_readiness"] == "not-ready"
    assert terminal["next_missing_step"]


def test_terminal_state_reports_blocked_when_payloads_are_nonexact(tmp_path):
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

    terminal = result["terminal_state"]
    assert terminal["status"] == "blocked"
    assert terminal["reason"] == "payloads-nonexact"
    assert terminal["input"] == {"n": "11413", "kind": "hostile-semiprime"}
    assert terminal["builder_readiness"] == "not-ready"
    assert terminal["known_support"] == [101, 103, 113]


def test_terminal_state_reports_built_for_exact_match(tmp_path):
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

    terminal = result["terminal_state"]
    assert terminal["status"] == "built"
    assert terminal["reason"] == "built-exact-match"
    assert terminal["builder_readiness"] == "ready"

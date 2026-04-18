import json
from pathlib import Path

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    try_refine_open_residual_state_with_policy_chain,
    try_seed_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_try_refine_open_residual_state_with_policy_chain_returns_first_progress():
    state = _load_state()

    result = try_refine_open_residual_state_with_policy_chain(
        state,
        [lambda s: None, _seed_a_with_101, _seed_b_with_113],
    )

    assert result is not None
    assert result["refiner"] == "_seed_a_with_101"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["state"]["slots"][1]["domain"]["candidates"] == []


def test_try_refine_open_residual_state_with_policy_chain_skips_non_applicable_refiner():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = try_refine_open_residual_state_with_policy_chain(
        state,
        [_seed_a_with_101, _seed_b_with_113],
    )

    assert result is not None
    assert result["refiner"] == "_seed_b_with_113"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["state"]["slots"][1]["domain"]["candidates"] == [113]


def test_try_refine_open_residual_state_with_policy_chain_returns_none_if_no_refiner_progresses():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = try_refine_open_residual_state_with_policy_chain(
        state,
        [_seed_a_with_101, _seed_b_with_113],
    )

    assert result is None

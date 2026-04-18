import json
from pathlib import Path

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    try_seed_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_try_seed_residual_state_slot_candidates_seeds_empty_slot():
    state = _load_state()

    seeded = try_seed_residual_state_slot_candidates(state, "a", [103, 101, 103])

    assert seeded is not None
    assert seeded["slots"][0]["domain"]["candidates"] == [101, 103]
    assert seeded["refinement"]["iteration"] == 1
    assert seeded["refinement"]["status"] == "open"
    assert seeded["refinement"]["payload_ready"] is False


def test_try_seed_residual_state_slot_candidates_returns_none_for_nonempty_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    seeded = try_seed_residual_state_slot_candidates(state, "a", [103])

    assert seeded is None

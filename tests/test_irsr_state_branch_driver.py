import json
from pathlib import Path

from pet.irsr_state import (
    branch_residual_state,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_branch_residual_state_returns_empty_for_fresh_state():
    state = _load_state()

    assert branch_residual_state(state) == []


def test_branch_residual_state_uses_selected_branch_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    branches = branch_residual_state(state)

    assert [branch["slots"][0]["domain"]["candidates"] for branch in branches] == [
        [101],
        [103],
    ]
    assert all(branch["slots"][1]["domain"]["candidates"] == [113] for branch in branches)


def test_branch_residual_state_returns_empty_for_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert branch_residual_state(state) == []

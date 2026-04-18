import json
from pathlib import Path

from pet.irsr_state import (
    choose_branch_slot,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_choose_branch_slot_returns_none_for_fresh_state():
    state = _load_state()

    assert choose_branch_slot(state) is None


def test_choose_branch_slot_returns_only_branchable_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert choose_branch_slot(state) == "a"


def test_choose_branch_slot_returns_first_branchable_slot_in_state_order():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    assert choose_branch_slot(state) == "a"


def test_choose_branch_slot_returns_none_for_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert choose_branch_slot(state) is None

import json
from pathlib import Path

from pet.irsr_state import (
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
    residual_state_branchable_slots,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_branchable_slots_is_empty_for_fresh_state():
    state = _load_state()

    assert residual_state_branchable_slots(state) == []


def test_residual_state_branchable_slots_reports_only_multi_candidate_slots():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert residual_state_branchable_slots(state) == ["a"]


def test_residual_state_branchable_slots_reports_multiple_slots_in_state_order():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    assert residual_state_branchable_slots(state) == ["a", "b"]


def test_residual_state_branchable_slots_is_empty_for_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert residual_state_branchable_slots(state) == []

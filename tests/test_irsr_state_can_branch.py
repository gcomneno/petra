import json
from pathlib import Path

from pet.irsr_state import (
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
    residual_state_can_branch_on_slot,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_can_branch_on_slot_is_false_for_empty_slot():
    state = _load_state()

    assert residual_state_can_branch_on_slot(state, "a") is False


def test_residual_state_can_branch_on_slot_is_false_for_singleton_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    assert residual_state_can_branch_on_slot(state, "a") is False


def test_residual_state_can_branch_on_slot_is_true_for_multi_candidate_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    assert residual_state_can_branch_on_slot(state, "a") is True


def test_residual_state_can_branch_on_slot_is_true_even_for_payload_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert residual_state_can_branch_on_slot(state, "a") is True


def test_residual_state_can_branch_on_slot_is_false_for_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert residual_state_can_branch_on_slot(state, "a") is False

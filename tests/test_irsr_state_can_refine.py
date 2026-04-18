import json
from pathlib import Path

from pet.irsr_state import (
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
    residual_state_can_refine,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_can_refine_is_true_for_open_state():
    state = _load_state()

    assert residual_state_can_refine(state) is True


def test_residual_state_can_refine_is_false_for_payload_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert residual_state_can_refine(state) is False


def test_residual_state_can_refine_is_false_for_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert residual_state_can_refine(state) is False

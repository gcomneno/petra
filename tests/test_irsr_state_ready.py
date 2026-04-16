import json
from pathlib import Path

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    residual_state_is_builder_ready,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_is_builder_ready_is_false_for_minimal_state():
    state = _load_state()

    assert residual_state_is_builder_ready(state) is False


def test_residual_state_is_builder_ready_is_true_for_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert residual_state_is_builder_ready(state) is True

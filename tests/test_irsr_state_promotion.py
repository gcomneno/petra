import json
from pathlib import Path

import pytest

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    residual_state_to_builder_payload,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_to_builder_payload_rejects_non_ready_state():
    state = _load_state()

    with pytest.raises(ValueError, match="missing-explicit-candidates"):
        residual_state_to_builder_payload(state)


def test_residual_state_to_builder_payload_promotes_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    builder_payload = residual_state_to_builder_payload(state)

    assert builder_payload == {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "prime_slots": [
            {"slot": "a", "candidates": [101]},
            {"slot": "b", "candidates": [113]},
        ],
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }

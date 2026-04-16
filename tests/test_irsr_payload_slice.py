import json
from pathlib import Path

from pet.irsr_payload_slice import residual_state_to_support_payload_slice


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_to_support_payload_slice_minimal_semiprime():
    state = _load_state()

    payload = residual_state_to_support_payload_slice(state)

    assert payload == {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "slots": [
            {
                "slot": "a",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
            {
                "slot": "b",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
        ],
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }


def test_residual_state_to_support_payload_slice_is_isolated_from_input_state():
    state = _load_state()

    payload = residual_state_to_support_payload_slice(state)
    payload["slots"][0]["domain"]["candidates"].append("fake-candidate")
    payload["slots"][0]["pet_hints"]["near_generator"].append("fake-hint")

    assert state["slots"][0]["domain"]["candidates"] == []
    assert state["slots"][0]["pet_hints"]["near_generator"] == []


def test_residual_state_to_support_payload_slice_excludes_non_payload_fields():
    state = _load_state()

    payload = residual_state_to_support_payload_slice(state)

    assert set(payload) == {
        "support_size",
        "exponent_profile",
        "slots",
        "joint_pet_constraints",
        "forbidden_patterns",
    }
    assert "target" not in payload
    assert "refinement" not in payload

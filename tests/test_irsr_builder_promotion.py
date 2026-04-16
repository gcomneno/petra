import json
from pathlib import Path

import pytest

from pet.irsr_payload_slice import (
    payload_slice_to_builder_payload,
    residual_state_to_support_payload_slice,
)


def _load_payload():
    state = json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )
    return residual_state_to_support_payload_slice(state)


def test_payload_slice_to_builder_payload_rejects_non_usable_slice():
    payload = _load_payload()

    with pytest.raises(ValueError, match="missing-explicit-candidates"):
        payload_slice_to_builder_payload(payload)


def test_payload_slice_to_builder_payload_promotes_explicit_candidates():
    payload = _load_payload()
    payload["slots"][0]["domain"]["candidates"] = [101]
    payload["slots"][1]["domain"]["candidates"] = [113]

    builder_payload = payload_slice_to_builder_payload(payload)

    assert builder_payload == {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "prime_slots": [
            {
                "slot": "a",
                "candidates": [101],
            },
            {
                "slot": "b",
                "candidates": [113],
            },
        ],
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }


def test_payload_slice_to_builder_payload_is_isolated_from_input_payload():
    payload = _load_payload()
    payload["slots"][0]["domain"]["candidates"] = [101]
    payload["slots"][1]["domain"]["candidates"] = [113]

    builder_payload = payload_slice_to_builder_payload(payload)
    builder_payload["prime_slots"][0]["candidates"].append(127)

    assert payload["slots"][0]["domain"]["candidates"] == [101]

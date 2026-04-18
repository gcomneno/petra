import json
from pathlib import Path

from pet.irsr_payload_slice import (
    payload_slice_builder_unusable_reasons,
    payload_slice_is_builder_usable,
    residual_state_to_support_payload_slice,
)


def _load_payload():
    state = json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )
    return residual_state_to_support_payload_slice(state)


def test_minimal_semiprime_payload_slice_is_not_builder_usable_yet():
    payload = _load_payload()

    assert payload_slice_is_builder_usable(payload) is False


def test_payload_slice_with_explicit_prime_candidates_is_builder_usable():
    payload = _load_payload()
    payload["slots"][0]["domain"]["candidates"] = [101]
    payload["slots"][1]["domain"]["candidates"] = [113]

    assert payload_slice_is_builder_usable(payload) is True


def test_builder_unusable_reasons_reports_missing_slot_candidates():
    payload = _load_payload()

    assert payload_slice_builder_unusable_reasons(payload) == [
        "slot:a:missing-explicit-candidates",
        "slot:b:missing-explicit-candidates",
    ]


def test_builder_unusable_reasons_is_empty_for_builder_usable_payload():
    payload = _load_payload()
    payload["slots"][0]["domain"]["candidates"] = [101]
    payload["slots"][1]["domain"]["candidates"] = [113]

    assert payload_slice_builder_unusable_reasons(payload) == []

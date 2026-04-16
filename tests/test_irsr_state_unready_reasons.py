import json
from pathlib import Path

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    residual_state_builder_unready_reasons,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_residual_state_builder_unready_reasons_reports_missing_slot_candidates():
    state = _load_state()

    assert residual_state_builder_unready_reasons(state) == [
        "slot:a:missing-explicit-candidates",
        "slot:b:missing-explicit-candidates",
    ]


def test_residual_state_builder_unready_reasons_is_empty_for_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert residual_state_builder_unready_reasons(state) == []

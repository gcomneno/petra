import json
from pathlib import Path

from pet.irsr_state import (
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_intersect_residual_state_slot_candidates_initializes_empty_slot():
    state = _load_state()

    refined = intersect_residual_state_slot_candidates(state, "a", [103, 101, 103])

    assert state["slots"][0]["domain"]["candidates"] == []
    assert refined["slots"][0]["domain"]["candidates"] == [101, 103]
    assert refined["refinement"]["iteration"] == 1
    assert refined["refinement"]["status"] == "open"
    assert refined["refinement"]["payload_ready"] is False


def test_intersect_residual_state_slot_candidates_intersects_existing_candidates():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])

    refined = intersect_residual_state_slot_candidates(state, "a", [103, 109])

    assert state["slots"][0]["domain"]["candidates"] == [101, 103, 107]
    assert refined["slots"][0]["domain"]["candidates"] == [103]
    assert refined["refinement"]["iteration"] == 2
    assert refined["refinement"]["status"] == "open"
    assert refined["refinement"]["payload_ready"] is False


def test_intersect_residual_state_slot_candidates_preserves_payload_ready_when_other_slot_ready():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    refined = intersect_residual_state_slot_candidates(state, "a", [103])

    assert refined["slots"][0]["domain"]["candidates"] == [103]
    assert refined["slots"][1]["domain"]["candidates"] == [113]
    assert refined["refinement"]["iteration"] == 3
    assert refined["refinement"]["status"] == "payload-ready"
    assert refined["refinement"]["payload_ready"] is True


def test_intersect_residual_state_slot_candidates_marks_contradiction_on_empty_intersection():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    refined = intersect_residual_state_slot_candidates(state, "a", [109])

    assert refined["slots"][0]["domain"]["candidates"] == []
    assert refined["refinement"]["iteration"] == 2
    assert refined["refinement"]["status"] == "contradiction"
    assert refined["refinement"]["payload_ready"] is False

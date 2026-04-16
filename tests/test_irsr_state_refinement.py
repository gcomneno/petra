import json
from pathlib import Path

from pet.irsr_state import refine_residual_state_slot_candidates


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_refine_residual_state_slot_candidates_updates_one_slot_and_iteration():
    state = _load_state()

    refined = refine_residual_state_slot_candidates(state, "a", [101, 103, 101])

    assert state["slots"][0]["domain"]["candidates"] == []
    assert refined["slots"][0]["domain"]["candidates"] == [101, 103]
    assert refined["slots"][1]["domain"]["candidates"] == []
    assert refined["refinement"]["iteration"] == 1
    assert refined["refinement"]["status"] == "open"
    assert refined["refinement"]["payload_ready"] is False


def test_refine_residual_state_slot_candidates_sets_payload_ready_when_all_slots_explicit():
    state = _load_state()

    refined = refine_residual_state_slot_candidates(state, "a", [101])
    refined = refine_residual_state_slot_candidates(refined, "b", [113])

    assert refined["slots"][0]["domain"]["candidates"] == [101]
    assert refined["slots"][1]["domain"]["candidates"] == [113]
    assert refined["refinement"]["iteration"] == 2
    assert refined["refinement"]["status"] == "payload-ready"
    assert refined["refinement"]["payload_ready"] is True

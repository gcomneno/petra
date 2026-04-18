import json
from pathlib import Path

from pet.irsr_state import (
    classify_residual_state,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_classify_residual_state_returns_open_for_fresh_state():
    state = _load_state()

    assert classify_residual_state(state) == "open"


def test_classify_residual_state_returns_branchable_for_multi_candidate_open_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    assert classify_residual_state(state) == "branchable"


def test_classify_residual_state_returns_payload_ready_for_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert classify_residual_state(state) == "payload-ready"


def test_classify_residual_state_returns_contradiction_for_dead_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    assert classify_residual_state(state) == "contradiction"

import json
from pathlib import Path

from pet.irsr_state import (
    summarize_residual_state_frontier,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_summarize_residual_state_frontier_reports_empty_frontier():
    assert summarize_residual_state_frontier([]) == {
        "total": 0,
        "open": 0,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }


def test_summarize_residual_state_frontier_counts_all_state_classes():
    open_state = _load_state()
    open_state = refine_residual_state_slot_candidates(open_state, "a", [101])

    branchable_state = _load_state()
    branchable_state = refine_residual_state_slot_candidates(branchable_state, "a", [101, 103])

    ready_state = _load_state()
    ready_state = refine_residual_state_slot_candidates(ready_state, "a", [101, 103])
    ready_state = refine_residual_state_slot_candidates(ready_state, "b", [113])

    contradiction_state = _load_state()
    contradiction_state = refine_residual_state_slot_candidates(contradiction_state, "a", [101, 103])
    contradiction_state = intersect_residual_state_slot_candidates(contradiction_state, "a", [109])

    summary = summarize_residual_state_frontier(
        [open_state, branchable_state, ready_state, contradiction_state]
    )

    assert summary == {
        "total": 4,
        "open": 1,
        "branchable": 1,
        "payload_ready": 1,
        "contradiction": 1,
    }

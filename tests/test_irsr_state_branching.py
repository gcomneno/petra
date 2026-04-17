import pytest
import json
from pathlib import Path

from pet.irsr_state import (
    branch_residual_state_on_slot_candidates,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_branch_residual_state_on_slot_candidates_splits_single_slot_candidates():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])

    branches = branch_residual_state_on_slot_candidates(state, "a")

    assert [branch["slots"][0]["domain"]["candidates"] for branch in branches] == [
        [101],
        [103],
        [107],
    ]
    assert all(branch["slots"][1]["domain"]["candidates"] == [] for branch in branches)


def test_branch_residual_state_on_slot_candidates_recomputes_ready_status_per_branch():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    branches = branch_residual_state_on_slot_candidates(state, "a")

    assert len(branches) == 2
    assert all(branch["refinement"]["status"] == "payload-ready" for branch in branches)
    assert all(branch["refinement"]["payload_ready"] is True for branch in branches)


def test_branch_residual_state_on_slot_candidates_does_not_alias_parent_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    branches = branch_residual_state_on_slot_candidates(state, "a")
    branches[0]["slots"][0]["domain"]["candidates"].append(999)

    assert state["slots"][0]["domain"]["candidates"] == [101, 103]


def test_branch_residual_state_on_slot_candidates_rejects_contradiction_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    with pytest.raises(ValueError, match="state is in contradiction"):
        branch_residual_state_on_slot_candidates(state, "a")


def test_branch_residual_state_on_slot_candidates_rejects_empty_slot():
    state = _load_state()

    with pytest.raises(ValueError, match="slot is not branchable"):
        branch_residual_state_on_slot_candidates(state, "a")


def test_branch_residual_state_on_slot_candidates_rejects_singleton_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    with pytest.raises(ValueError, match="slot is not branchable"):
        branch_residual_state_on_slot_candidates(state, "a")

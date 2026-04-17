import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_frontier_once,
    build_next_residual_state_frontier,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_build_next_residual_state_frontier_keeps_empty_frontier_empty():
    step = advance_residual_state_frontier_once([])

    assert build_next_residual_state_frontier(step) == []


def test_build_next_residual_state_frontier_requeues_emitted_after_remaining():
    first = _load_state()
    first = refine_residual_state_slot_candidates(first, "a", [101, 103])

    second = _load_state()
    second = refine_residual_state_slot_candidates(second, "a", [211])

    step = advance_residual_state_frontier_once([first, second])
    next_frontier = build_next_residual_state_frontier(step)

    assert len(next_frontier) == 3
    assert next_frontier[0]["slots"][0]["domain"]["candidates"] == [211]
    assert next_frontier[1]["slots"][0]["domain"]["candidates"] == [101]
    assert next_frontier[2]["slots"][0]["domain"]["candidates"] == [103]


def test_build_next_residual_state_frontier_drops_promoted_and_stopped_states():
    ready = _load_state()
    ready = refine_residual_state_slot_candidates(ready, "a", [101, 103])
    ready = refine_residual_state_slot_candidates(ready, "b", [113])

    dead = _load_state()
    dead = refine_residual_state_slot_candidates(dead, "a", [101, 103])
    dead = intersect_residual_state_slot_candidates(dead, "a", [109])

    assert build_next_residual_state_frontier(
        advance_residual_state_frontier_once([ready])
    ) == []
    assert build_next_residual_state_frontier(
        advance_residual_state_frontier_once([dead])
    ) == []


def test_build_next_residual_state_frontier_requeues_idle_states():
    idle = _load_state()
    idle = refine_residual_state_slot_candidates(idle, "a", [101])

    step = advance_residual_state_frontier_once([idle])
    next_frontier = build_next_residual_state_frontier(step)

    assert len(next_frontier) == 1
    assert next_frontier[0]["slots"][0]["domain"]["candidates"] == [101]

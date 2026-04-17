import json
from pathlib import Path

from pet.irsr_state import (
    make_intersect_first_branchable_slot_policy,
    make_intersect_slot_policy,
    refine_residual_state_slot_candidates,
    try_intersect_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_try_intersect_residual_state_slot_candidates_returns_none_for_empty_slot():
    state = _load_state()

    refined = try_intersect_residual_state_slot_candidates(state, "a", [101])

    assert refined is None


def test_try_intersect_residual_state_slot_candidates_returns_none_when_no_actual_narrowing():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    refined = try_intersect_residual_state_slot_candidates(state, "a", [101, 103])

    assert refined is None


def test_try_intersect_residual_state_slot_candidates_narrows_nonempty_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    refined = try_intersect_residual_state_slot_candidates(state, "a", [103, 109])

    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [103]
    assert refined["refinement"]["iteration"] == 2


def test_make_intersect_slot_policy_targets_requested_slot_only():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    policy = make_intersect_slot_policy("b", [127], policy_name="narrow-b-127")
    refined = policy(state)

    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [101, 103]
    assert refined["slots"][1]["domain"]["candidates"] == [127]
    assert policy.__name__ == "narrow-b-127"


def test_make_intersect_first_branchable_slot_policy_uses_first_branchable_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    policy = make_intersect_first_branchable_slot_policy(
        [103], policy_name="narrow-first-branchable"
    )
    refined = policy(state)

    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [103]
    assert refined["slots"][1]["domain"]["candidates"] == [113, 127]
    assert policy.__name__ == "narrow-first-branchable"

import json
from pathlib import Path

from pet.irsr_state import (
    branchable_residual_state_slot_widths,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    select_first_branchable_slot,
    select_max_width_branchable_slot,
    select_min_width_branchable_slot,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_branchable_residual_state_slot_widths_reports_only_branchable_slots():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    assert branchable_residual_state_slot_widths(state) == [
        {"slot": "a", "candidate_count": 3},
    ]


def test_branchable_residual_state_slot_widths_preserves_state_order():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127, 131])

    assert branchable_residual_state_slot_widths(state) == [
        {"slot": "a", "candidate_count": 2},
        {"slot": "b", "candidate_count": 3},
    ]


def test_select_first_branchable_slot_returns_first_in_state_order():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127, 131])

    assert select_first_branchable_slot(state) == "a"


def test_select_min_width_branchable_slot_returns_smallest_domain():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127])

    assert select_min_width_branchable_slot(state) == "b"


def test_select_max_width_branchable_slot_returns_largest_domain():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113, 127, 131])

    assert select_max_width_branchable_slot(state) == "b"


def test_selectors_return_none_when_no_branchable_slots_exist():
    state = _load_state()

    assert select_first_branchable_slot(state) is None
    assert select_min_width_branchable_slot(state) is None
    assert select_max_width_branchable_slot(state) is None

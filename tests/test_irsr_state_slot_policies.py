import json
from pathlib import Path

from pet.irsr_state import (
    empty_residual_state_slots,
    make_hostile_semiprime_residual_state,
    make_seed_first_empty_slot_policy,
    make_seed_slot_policy,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_empty_residual_state_slots_reports_all_empty_slots_in_order():
    state = _load_state()

    assert empty_residual_state_slots(state) == ["a", "b"]


def test_empty_residual_state_slots_skips_initialized_slots():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    assert empty_residual_state_slots(state) == ["b"]


def test_make_seed_slot_policy_seeds_only_requested_slot():
    state = _load_state()
    policy = make_seed_slot_policy("b", [113], policy_name="seed-b-113")

    refined = policy(state)

    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == []
    assert refined["slots"][1]["domain"]["candidates"] == [113]


def test_make_seed_slot_policy_returns_none_when_requested_slot_is_not_empty():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "b", [113])
    policy = make_seed_slot_policy("b", [127], policy_name="seed-b-127")

    refined = policy(state)

    assert refined is None


def test_make_seed_slot_policy_exposes_requested_name():
    policy = make_seed_slot_policy("a", [101], policy_name="seed-a-101")

    assert policy.__name__ == "seed-a-101"


def test_make_seed_first_empty_slot_policy_seeds_first_available_slot():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    policy = make_seed_first_empty_slot_policy([113], policy_name="seed-first-empty")
    refined = policy(state)

    assert refined is not None
    assert refined["slots"][0]["domain"]["candidates"] == [101]
    assert refined["slots"][1]["domain"]["candidates"] == [113]


def test_make_seed_first_empty_slot_policy_returns_none_when_no_empty_slots_remain():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    policy = make_seed_first_empty_slot_policy([127], policy_name="seed-first-empty")
    refined = policy(state)

    assert refined is None

from copy import deepcopy

from pet.irsr_state import (
    is_residual_state_progress_acceptable,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    summarize_residual_state_progress,
    try_accept_refined_residual_state,
    try_seed_residual_state_slot_candidates,
    intersect_residual_state_slot_candidates,
)


def test_summarize_residual_state_progress_accepts_empty_slot_reduction():
    before = make_hostile_semiprime_residual_state(11413)
    after = try_seed_residual_state_slot_candidates(before, "a", [101])

    progress = summarize_residual_state_progress(before, after)

    assert progress == {
        "candidate_count_delta": 1,
        "empty_slot_count_delta": -1,
        "branchable_slot_count_delta": 0,
        "payload_ready_changed": False,
        "entered_contradiction": False,
    }
    assert is_residual_state_progress_acceptable(progress) is True


def test_summarize_residual_state_progress_accepts_candidate_reduction():
    before = make_hostile_semiprime_residual_state(11413)
    before = refine_residual_state_slot_candidates(before, "a", [101, 103])

    after = intersect_residual_state_slot_candidates(before, "a", [103])

    progress = summarize_residual_state_progress(before, after)

    assert progress == {
        "candidate_count_delta": -1,
        "empty_slot_count_delta": 0,
        "branchable_slot_count_delta": -1,
        "payload_ready_changed": False,
        "entered_contradiction": False,
    }
    assert is_residual_state_progress_acceptable(progress) is True


def test_summarize_residual_state_progress_accepts_payload_ready_transition():
    before = make_hostile_semiprime_residual_state(11413)
    before = refine_residual_state_slot_candidates(before, "a", [101])

    after = try_seed_residual_state_slot_candidates(before, "b", [113])

    progress = summarize_residual_state_progress(before, after)

    assert progress == {
        "candidate_count_delta": 1,
        "empty_slot_count_delta": -1,
        "branchable_slot_count_delta": 0,
        "payload_ready_changed": True,
        "entered_contradiction": False,
    }
    assert is_residual_state_progress_acceptable(progress) is True


def test_summarize_residual_state_progress_rejects_contradiction():
    before = make_hostile_semiprime_residual_state(11413)
    before = refine_residual_state_slot_candidates(before, "a", [101, 103])

    after = intersect_residual_state_slot_candidates(before, "a", [109])

    progress = summarize_residual_state_progress(before, after)

    assert progress == {
        "candidate_count_delta": -2,
        "empty_slot_count_delta": 1,
        "branchable_slot_count_delta": -1,
        "payload_ready_changed": False,
        "entered_contradiction": True,
    }
    assert is_residual_state_progress_acceptable(progress) is False


def test_try_accept_refined_residual_state_rejects_cosmetic_change():
    before = make_hostile_semiprime_residual_state(11413)
    after = deepcopy(before)
    after["slots"][0]["pet_hints"]["near_generator"].append("cosmetic")

    accepted = try_accept_refined_residual_state(before, after)

    assert accepted is None


def test_try_accept_refined_residual_state_returns_progress_for_real_refinement():
    before = make_hostile_semiprime_residual_state(11413)
    after = try_seed_residual_state_slot_candidates(before, "a", [101])

    accepted = try_accept_refined_residual_state(before, after)

    assert accepted is not None
    assert accepted["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert accepted["progress"] == {
        "candidate_count_delta": 1,
        "empty_slot_count_delta": -1,
        "branchable_slot_count_delta": 0,
        "payload_ready_changed": False,
        "entered_contradiction": False,
    }

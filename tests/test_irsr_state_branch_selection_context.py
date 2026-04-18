from pet.irsr_state import (
    build_branch_selection_context,
    context_score_by_candidate_count,
    context_score_by_hint_density,
    context_score_by_total_hint_count,
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
)


def _make_state():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 103, 107])
    state["slots"][0]["pet_hints"]["near_generator"] = ["g1"]
    state["slots"][0]["pet_hints"]["block_shape"] = []

    state = refine_residual_state_slot_candidates(state, "b", [113, 127])
    state["slots"][1]["pet_hints"]["near_generator"] = ["g1", "g2"]
    state["slots"][1]["pet_hints"]["block_shape"] = ["s1"]

    return state


def test_build_branch_selection_context_reports_branchable_slot_data():
    state = _make_state()

    context = build_branch_selection_context(state)

    assert context == {
        "branchable_slots": ["a", "b"],
        "slot_data": {
            "a": {
                "candidate_count": 3,
                "near_generator_hint_count": 1,
                "block_shape_hint_count": 0,
                "total_hint_count": 1,
            },
            "b": {
                "candidate_count": 2,
                "near_generator_hint_count": 2,
                "block_shape_hint_count": 1,
                "total_hint_count": 3,
            },
        },
    }


def test_context_score_by_candidate_count_reads_prebuilt_context():
    context = build_branch_selection_context(_make_state())

    assert context_score_by_candidate_count(context, "a") == 3
    assert context_score_by_candidate_count(context, "b") == 2


def test_context_score_by_total_hint_count_reads_prebuilt_context():
    context = build_branch_selection_context(_make_state())

    assert context_score_by_total_hint_count(context, "a") == 1
    assert context_score_by_total_hint_count(context, "b") == 3


def test_context_score_by_hint_density_computes_hint_per_candidate_ratio():
    context = build_branch_selection_context(_make_state())

    assert context_score_by_hint_density(context, "a") == 1 / 3
    assert context_score_by_hint_density(context, "b") == 3 / 2

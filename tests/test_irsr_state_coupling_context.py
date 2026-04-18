from pet.irsr_state import (
    build_coupling_aware_branch_selection_context,
    context_score_by_coupling_mentions,
    context_score_by_coupling_weighted_hint_density,
)


def _make_state():
    return {
        "target": {"n": "synthetic"},
        "skeleton": {
            "support_size": 3,
            "exponent_profile": [1, 1, 1],
            "squarefree": True,
            "normalized_order": "a<=b<=c",
        },
        "slots": [
            {
                "slot": "a",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [101, 103, 107],
                },
                "pet_hints": {
                    "near_generator": ["g1"],
                    "block_shape": [],
                },
            },
            {
                "slot": "b",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [113, 127],
                },
                "pet_hints": {
                    "near_generator": ["g1", "g2"],
                    "block_shape": ["s1"],
                },
            },
            {
                "slot": "c",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
        ],
        "coupling": {
            "product_constraint": "a*b*c=n",
            "joint_pet_constraints": [
                "a linked to b",
                "prefer b compatibility",
            ],
            "forbidden_patterns": [
                "forbid a collision",
                "forbid b overload",
                "forbid b mismatch",
            ],
        },
        "refinement": {
            "iteration": 0,
            "status": "open",
            "payload_ready": False,
        },
    }


def test_build_coupling_aware_branch_selection_context_reports_slot_specific_coupling_data():
    context = build_coupling_aware_branch_selection_context(_make_state())

    assert context == {
        "branchable_slots": ["a", "b"],
        "slot_data": {
            "a": {
                "candidate_count": 3,
                "near_generator_hint_count": 1,
                "block_shape_hint_count": 0,
                "total_hint_count": 1,
                "joint_constraint_mentions": 1,
                "forbidden_pattern_mentions": 1,
                "coupling_mentions": 2,
            },
            "b": {
                "candidate_count": 2,
                "near_generator_hint_count": 2,
                "block_shape_hint_count": 1,
                "total_hint_count": 3,
                "joint_constraint_mentions": 2,
                "forbidden_pattern_mentions": 2,
                "coupling_mentions": 4,
            },
        },
        "global": {
            "joint_constraint_count": 2,
            "forbidden_pattern_count": 3,
        },
    }


def test_context_score_by_coupling_mentions_reads_prebuilt_context():
    context = build_coupling_aware_branch_selection_context(_make_state())

    assert context_score_by_coupling_mentions(context, "a") == 2
    assert context_score_by_coupling_mentions(context, "b") == 4


def test_context_score_by_coupling_weighted_hint_density_prefers_tighter_more_coupled_slot():
    context = build_coupling_aware_branch_selection_context(_make_state())

    assert context_score_by_coupling_weighted_hint_density(context, "a") == 3 / 3
    assert context_score_by_coupling_weighted_hint_density(context, "b") == 7 / 2

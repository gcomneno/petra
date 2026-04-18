from pet.irsr_state import (
    make_weighted_branch_selector,
    make_weighted_slot_scorer,
    score_by_block_shape_hint_count,
    score_by_candidate_count,
    score_by_near_generator_hint_count,
    score_by_total_hint_count,
    select_scored_branchable_slot,
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
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        },
        "refinement": {
            "iteration": 0,
            "status": "open",
            "payload_ready": False,
        },
    }


def test_hint_count_scorers_report_expected_counts():
    state = _make_state()

    assert score_by_near_generator_hint_count(state, "a") == 1
    assert score_by_near_generator_hint_count(state, "b") == 2
    assert score_by_block_shape_hint_count(state, "a") == 0
    assert score_by_block_shape_hint_count(state, "b") == 1
    assert score_by_total_hint_count(state, "a") == 1
    assert score_by_total_hint_count(state, "b") == 3


def test_make_weighted_slot_scorer_combines_multiple_signals():
    state = _make_state()

    scorer = make_weighted_slot_scorer(
        [
            (score_by_candidate_count, -1),
            (score_by_total_hint_count, 10),
        ],
        scorer_name="hint-heavy-scorer",
    )

    assert scorer.__name__ == "hint-heavy-scorer"
    assert scorer(state, "a") == 7
    assert scorer(state, "b") == 28


def test_weighted_branch_selector_can_prefer_higher_composite_score():
    state = _make_state()

    selector = make_weighted_branch_selector(
        [
            (score_by_candidate_count, -1),
            (score_by_total_hint_count, 10),
        ],
        maximize=True,
        selector_name="prefer-hints",
    )

    assert selector.__name__ == "prefer-hints"
    assert selector(state) == "b"


def test_weighted_branch_selector_can_prefer_lower_composite_score():
    state = _make_state()

    selector = make_weighted_branch_selector(
        [
            (score_by_candidate_count, 1),
            (score_by_total_hint_count, 10),
        ],
        maximize=False,
        selector_name="prefer-lower-score",
    )

    assert selector(state) == "a"


def test_select_scored_branchable_slot_works_with_weighted_slot_scorer():
    state = _make_state()

    scorer = make_weighted_slot_scorer(
        [
            (score_by_candidate_count, 1),
            (score_by_total_hint_count, -5),
        ],
        scorer_name="prefer-tight-and-hinted",
    )

    assert select_scored_branchable_slot(state, scorer, maximize=False) == "b"

import json
from pathlib import Path

from pet.irsr_state import make_hostile_semiprime_residual_state


def test_make_hostile_semiprime_residual_state_matches_minimal_contract():
    state = make_hostile_semiprime_residual_state(11413)

    assert set(state) == {"target", "skeleton", "slots", "coupling", "refinement"}

    assert state["target"] == {"n": "11413"}

    assert state["skeleton"] == {
        "support_size": 2,
        "exponent_profile": [1, 1],
        "squarefree": True,
        "normalized_order": "a<=b",
    }

    assert state["slots"] == [
        {
            "slot": "a",
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
        {
            "slot": "b",
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
    ]

    assert state["coupling"] == {
        "product_constraint": "a*b=n",
        "joint_pet_constraints": [],
        "forbidden_patterns": [],
    }

    assert state["refinement"] == {
        "iteration": 0,
        "status": "open",
        "payload_ready": False,
    }


def test_make_hostile_semiprime_residual_state_matches_fixture_shape():
    expected = json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )
    actual = make_hostile_semiprime_residual_state(expected["target"]["n"])

    assert actual == expected

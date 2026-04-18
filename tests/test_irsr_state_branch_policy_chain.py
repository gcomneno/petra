import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_once_with_prebranch_policy_chain,
    make_intersect_first_branchable_slot_policy,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_advance_residual_state_once_with_prebranch_policy_chain_refines_branchable_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = advance_residual_state_once_with_prebranch_policy_chain(
        state,
        open_refiners=[],
        branch_refiners=[
            make_intersect_first_branchable_slot_policy(
                [103], policy_name="narrow-first-branchable"
            )
        ],
    )

    assert result["action"] == "refine"
    assert result["refiner"] == "narrow-first-branchable"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [103]
    assert result["state"]["slots"][1]["domain"]["candidates"] == []
    assert result["state"]["refinement"]["status"] == "open"


def test_advance_residual_state_once_with_prebranch_policy_chain_falls_back_to_branch():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = advance_residual_state_once_with_prebranch_policy_chain(
        state,
        open_refiners=[],
        branch_refiners=[
            make_intersect_first_branchable_slot_policy(
                [101, 103], policy_name="no-op-branch-refiner"
            )
        ],
    )

    assert result["action"] == "branch"
    assert result["slot"] == "a"
    assert [branch["slots"][0]["domain"]["candidates"] for branch in result["branches"]] == [
        [101],
        [103],
    ]

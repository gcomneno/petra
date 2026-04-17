from pet.irsr_state import (
    make_hostile_semiprime_residual_state,
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence,
)


def test_factory_built_state_can_flow_through_current_irsr_runner():
    state = make_hostile_semiprime_residual_state(11413)
    state = refine_residual_state_slot_candidates(state, "a", [101, 113])

    result = run_residual_state_frontier_until_quiescence([state], 5)

    assert result["steps_run"] == 3
    assert result["termination_reason"] == "quiescent-idle-frontier"
    assert result["frontier_summary"] == {
        "total": 2,
        "open": 2,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["trace"] == [
        {"step": 1, "action": "branch", "emitted": 2},
        {"step": 2, "action": "idle"},
        {"step": 3, "action": "idle"},
    ]

from __future__ import annotations

from pet.guarded_redirect import build_row


def test_guarded_redirect_backend_completes_known_flat_k_case() -> None:
    row = build_row(357357, 4)

    assert row["guard_decision"] == "would-redirect-to-shadow-anchor"
    assert row["guard_reason"] == "structural-prefix-trap-active-shadow"
    assert row["current_anchor"] == "231"
    assert row["shadow_anchor"] == "3"
    assert row["structural_prefix"] == "77"
    assert row["expanded_execution_delta"] == "redirect-completes-with-flat-k"
    assert row["redirect_flat_k_chain"] == "3 * 7 * 7 * 17 * 11 * 13"
    assert row["redirect_flat_k_terminal_residual"] == "1"


def test_guarded_redirect_backend_keeps_completed_lateral_door() -> None:
    row = build_row(30030, 4)

    assert row["guard_decision"] == "keep-current"
    assert row["guard_reason"] == "not-blocked-status"
    assert row["expanded_execution_delta"] == "guard-not-triggered"
    assert row["current_chain"] == "5005 * 2 * 3"
    assert row["current_terminal_residual"] == "1"

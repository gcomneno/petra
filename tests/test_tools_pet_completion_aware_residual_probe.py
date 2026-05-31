from __future__ import annotations

import pytest
import json
import subprocess
import sys
from typing import Any


pytestmark = pytest.mark.slow


def run_probe(n: int, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_completion_aware_residual_probe.py",
            str(n),
            *args,
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return json.loads(result.stdout)


def test_completion_aware_probe_marks_selected_trap_door_candidate() -> None:
    probe = run_probe(21021)

    assert probe["schema"] == "pet.completion_aware_residual_probe.v0"
    assert probe["n"] == 21021
    assert probe["status"] == "blocked-no-verified-anchor"
    assert probe["selected_anchor"] == "21"
    assert probe["selected_residual"] == "1001"
    assert probe["terminal_residual"] == "1001"

    selected = next(
        row for row in probe["candidates"] if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual"] == "1001"
    assert selected["residual_final_status"] == "flat-k-scan-required"
    assert selected["classification"] == "selected-trap-door-candidate"


def test_completion_aware_probe_marks_lateral_door_candidate() -> None:
    probe = run_probe(30030)

    assert probe["status"] == "complete"
    assert probe["selected_anchor"] == "5005"
    assert probe["selected_residual"] == "6"
    assert probe["terminal_residual"] == "1"

    selected = next(
        row for row in probe["candidates"] if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual"] == "6"
    assert selected["residual_final_status"] == "solved-by-same-shape-scan"
    assert selected["classification"] == "completion-friendly"


def test_completion_aware_probe_reflects_flat_k_profile() -> None:
    probe = run_probe(21021, "--auto-flat-k-scan")

    assert probe["profile"]["auto_flat_k_scan"] is True
    assert probe["status"] == "complete"
    assert probe["selected_anchor"] == "21"
    assert probe["selected_residual"] == "1001"
    assert probe["terminal_residual"] == "1"

    selected = next(
        row for row in probe["candidates"] if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual_final_status"] == "partial-factorization-by-flat-k-scan"
    assert selected["classification"] == "expandable-with-active-mode"


def test_completion_aware_probe_compares_expanded_profiles() -> None:
    probe = run_probe(21021, "--compare-expanded-profile")

    assert probe["profile"]["compare_expanded_profile"] is True

    selected = next(
        row for row in probe["candidates"] if row["anchor"] == probe["selected_anchor"]
    )

    comparison = selected["expanded_profile_comparison"]

    assert comparison["flat_k"]["status"] == "complete"
    assert comparison["flat_k"]["terminal_residual"] == "1"
    assert comparison["completion_delta"] == "opens-with-flat-k"


def test_completion_aware_probe_exposes_357357_selected_trap_door() -> None:
    probe = run_probe(357357, "--compare-expanded-profile")

    assert probe["status"] == "blocked-no-verified-anchor"
    assert probe["selected_anchor"] == "231"
    assert probe["selected_residual"] == "1547"

    alternative = next(row for row in probe["candidates"] if row["anchor"] == "3")
    selected = next(row for row in probe["candidates"] if row["anchor"] == "231")

    assert alternative["classification"] == "expandable-with-active-mode"
    assert alternative["expanded_profile_comparison"]["completion_delta"] == (
        "opens-with-flat-k"
    )

    assert selected["classification"] == "selected-trap-door-candidate"
    assert selected["expanded_profile_comparison"]["completion_delta"] == (
        "opens-with-flat-k"
    )


def test_completion_aware_probe_reports_active_completion_signal() -> None:
    probe = run_probe(21021)

    by_anchor = {row["anchor"]: row for row in probe["candidates"]}

    assert by_anchor["3"]["active_completion_signal"] == (
        "inactive-shape-family-required"
    )
    assert by_anchor["21"]["active_completion_signal"] == ("inactive-flat-k-required")


def test_completion_aware_probe_distinguishes_357357_active_signal() -> None:
    probe = run_probe(357357, "--compare-expanded-profile")

    by_anchor = {row["anchor"]: row for row in probe["candidates"]}

    assert by_anchor["3"]["classification"] == "expandable-with-active-mode"
    assert by_anchor["3"]["active_completion_signal"] == ("active-partial-expandable")
    assert by_anchor["3"]["expanded_profile_comparison"]["completion_delta"] == (
        "opens-with-flat-k"
    )

    assert by_anchor["231"]["classification"] == "selected-trap-door-candidate"
    assert by_anchor["231"]["active_completion_signal"] == ("inactive-flat-k-required")
    assert by_anchor["231"]["expanded_profile_comparison"]["completion_delta"] == (
        "opens-with-flat-k"
    )


def test_completion_aware_probe_shadow_ranking_suggests_357357_alternative() -> None:
    probe = run_probe(357357, "--compare-ranking-policy")

    ranking = probe["ranking_policy_comparison"]

    assert probe["profile"]["compare_ranking_policy"] is True
    assert ranking["policy"] == "research-shadow-active-completion-v0"
    assert ranking["current_selected_anchor"] == "231"
    assert ranking["current_selected_residual"] == "1547"
    assert ranking["suggested_anchor"] == "3"
    assert ranking["suggested_residual"] == "119119"
    assert ranking["changed_selection"] is True
    assert ranking["reason"] == (
        "active-partial-expandable beats inactive-flat-k-required"
    )

    by_anchor = {row["anchor"]: row for row in probe["candidates"]}

    assert by_anchor["3"]["completion_aware_rank"] == "1"
    assert by_anchor["231"]["completion_aware_rank"] == "2"


def test_completion_aware_probe_shadow_ranking_keeps_lateral_door() -> None:
    probe = run_probe(30030, "--compare-ranking-policy")

    ranking = probe["ranking_policy_comparison"]

    assert ranking["current_selected_anchor"] == "5005"
    assert ranking["suggested_anchor"] == "5005"
    assert ranking["changed_selection"] is False
    assert ranking["reason"] == (
        "current-selection-matches-completion-aware-shadow-ranking"
    )


def test_completion_aware_probe_shadow_ranking_handles_no_candidates() -> None:
    probe = run_probe(1001, "--compare-ranking-policy")

    ranking = probe["ranking_policy_comparison"]

    assert ranking["current_selected_anchor"] == "-"
    assert ranking["suggested_anchor"] == "-"
    assert ranking["changed_selection"] is False
    assert ranking["reason"] == "no-depth-0-candidates"

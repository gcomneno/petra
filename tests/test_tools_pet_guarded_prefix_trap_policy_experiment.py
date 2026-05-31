from __future__ import annotations

import pytest
import json
import subprocess
import sys


pytestmark = pytest.mark.slow


def run_experiment(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/research/pet_guarded_prefix_trap_policy_experiment.py",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_guarded_prefix_trap_experiment_marks_known_redirect() -> None:
    result = run_experiment(
        "--walls",
        "17017",
        "--contexts",
        "21",
        "--redirect-only",
    )

    lines = result.stdout.strip().splitlines()

    assert lines[0].startswith("wall\tcontext\tn\tstatus")
    assert len(lines) == 2
    assert "17017\t21\t357357" in lines[1]
    assert "\t231\t1547\t3\t119119\t77\t" in lines[1]
    assert "\tinactive-flat-k-required\tactive-partial-expandable\t" in lines[1]
    assert "\twould-redirect-to-shadow-anchor\t" in lines[1]
    assert "structural-prefix-trap-active-shadow" in lines[1]


def test_guarded_prefix_trap_experiment_keeps_completed_lateral_door() -> None:
    result = run_experiment(
        "--walls",
        "1001",
        "--contexts",
        "30",
        "--redirect-only",
    )

    lines = result.stdout.strip().splitlines()

    assert lines == [
        "wall\tcontext\tn\tstatus\tcurrent_anchor\tcurrent_residual\t"
        "shadow_anchor\tshadow_residual\tstructural_prefix\t"
        "current_signal\tshadow_signal\tguard_decision\tguard_reason\t"
        "candidate_count"
    ]


def test_guarded_prefix_trap_experiment_can_emit_json() -> None:
    result = run_experiment(
        "--walls",
        "17017",
        "--contexts",
        "21",
        "--redirect-only",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.guarded_prefix_trap_policy_experiment.v0"
    assert payload["profile"]["redirect_only"] is True
    assert payload["rows"][0]["wall"] == 17017
    assert payload["rows"][0]["context"] == 21
    assert payload["rows"][0]["n"] == 357357
    assert payload["rows"][0]["current_anchor"] == "231"
    assert payload["rows"][0]["shadow_anchor"] == "3"
    assert payload["rows"][0]["structural_prefix"] == "77"
    assert payload["rows"][0]["guard_decision"] == ("would-redirect-to-shadow-anchor")

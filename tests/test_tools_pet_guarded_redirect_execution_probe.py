from __future__ import annotations

import json
import subprocess
import sys


def run_probe(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/research/pet_guarded_redirect_execution_probe.py",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_guarded_redirect_execution_probe_runs_known_guard_case() -> None:
    result = run_probe("357357", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]

    assert payload["schema"] == "pet.guarded_redirect_execution_probe.v0"
    assert row["n"] == 357357
    assert row["current_status"] == "blocked-no-verified-anchor"
    assert row["current_anchor"] == "231"
    assert row["shadow_anchor"] == "3"
    assert row["structural_prefix"] == "77"
    assert row["guard_decision"] == "would-redirect-to-shadow-anchor"
    assert row["guard_reason"] == "structural-prefix-trap-active-shadow"
    assert row["redirect_status"] != "-"
    assert row["redirect_chain"].startswith("3 * ")
    assert row["execution_delta"] in {
        "redirect-completes",
        "redirect-expands-route",
        "redirect-remains-blocked",
    }


def test_guarded_redirect_execution_probe_keeps_positive_control() -> None:
    result = run_probe("30030", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]

    assert row["n"] == 30030
    assert row["guard_decision"] == "keep-current"
    assert row["execution_delta"] == "guard-not-triggered"
    assert row["redirect_status"] == "-"
    assert row["redirect_chain"] == "-"


def test_guarded_redirect_execution_probe_text_output() -> None:
    result = run_probe("357357")

    assert "PET GUARDED REDIRECT EXECUTION PROBE" in result.stdout
    assert "guard_decision = would-redirect-to-shadow-anchor" in result.stdout
    assert "shadow_anchor = 3" in result.stdout
    assert "redirect_chain = 3 * " in result.stdout

def test_guarded_redirect_execution_probe_completes_with_flat_k() -> None:
    result = run_probe("357357", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]

    assert row["guard_decision"] == "would-redirect-to-shadow-anchor"
    assert row["execution_delta"] == "redirect-expands-route"
    assert row["redirect_flat_k_status"] == "complete"
    assert row["redirect_flat_k_terminal_residual"] == "1"
    assert row["redirect_flat_k_chain"].startswith("3 * ")
    assert row["expanded_execution_delta"] == "redirect-completes-with-flat-k"


def test_guarded_redirect_execution_probe_reports_expanded_guard_not_triggered() -> None:
    result = run_probe("30030", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]

    assert row["guard_decision"] == "keep-current"
    assert row["execution_delta"] == "guard-not-triggered"
    assert row["expanded_execution_delta"] == "guard-not-triggered"
    assert row["redirect_flat_k_status"] == "-"
    assert row["redirect_shape_family_status"] == "-"


def test_guarded_redirect_execution_probe_reports_factor_chain_certificates() -> None:
    result = run_probe("357357", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]
    certificates = row["factor_chain_certificates"]

    assert certificates["current"]["kind"] == "factor-chain"
    assert certificates["current"]["verified_product"] is True
    assert certificates["current"]["product"] == 357357

    assert certificates["redirect"]["verified_product"] is True
    assert certificates["redirect"]["product"] == 357357

    assert certificates["redirect_flat_k"]["verified_product"] is True
    assert certificates["redirect_flat_k"]["product"] == 357357
    assert certificates["redirect_flat_k"]["status"] == "verified-product"

    assert "not a PET operator-path certificate" in certificates[
        "redirect_flat_k"
    ]["claim"]


def test_guarded_redirect_execution_probe_marks_unavailable_factor_chain() -> None:
    result = run_probe("30030", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]
    certificates = row["factor_chain_certificates"]

    assert certificates["current"]["verified_product"] is True
    assert certificates["redirect"]["status"] == "unavailable"
    assert certificates["redirect"]["verified_product"] is False
    assert certificates["redirect"]["product"] is None


def test_guarded_redirect_execution_probe_certifies_shape_family_completion() -> None:
    result = run_probe("374374", "--json")

    payload = json.loads(result.stdout)
    row = payload["rows"][0]
    certificates = row["factor_chain_certificates"]

    assert row["guard_decision"] == "would-redirect-to-shadow-anchor"
    assert row["execution_delta"] == "redirect-expands-route"
    assert row["expanded_execution_delta"] == "redirect-completes-with-shape-family"

    assert row["redirect_shape_family_status"] == "complete"
    assert row["redirect_shape_family_terminal_residual"] == "1"
    assert row["redirect_shape_family_chain"] == "2 * 7 * 187 * 11 * 13"

    certificate = certificates["redirect_shape_family"]
    assert certificate["status"] == "verified-product"
    assert certificate["verified_product"] is True
    assert certificate["product"] == 374374
    assert certificate["factors"] == [2, 7, 187, 11, 13]

    assert certificates["redirect_flat_k"]["verified_product"] is True
    assert certificates["redirect_flat_k"]["chain"] == "2 * 7 * 26741"

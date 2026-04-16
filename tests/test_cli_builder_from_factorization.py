from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_cli_builder_from_factorization_json_smoke(tmp_path) -> None:
    path = tmp_path / "factors.json"
    path.write_text(json.dumps({"factors": [[3, 1], [5, 1], [7, 1]]}), encoding="utf-8")

    out = _run_cli("builder-from-factorization", str(path), "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-builder-from-factorization-v0"
    assert payload["input_n"] == 105
    assert payload["support_report"]["builder_readiness"] == "ready"
    assert payload["support_report"]["exact_target_match"] is True
    assert payload["final_build_output"]["build_status"] == "built"

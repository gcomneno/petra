import json
import subprocess
import sys


def _run_json(*args, cwd=None):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
        cwd=cwd,
    )
    return json.loads(out)


def test_cli_backbone_cache_build_and_inspect(tmp_path):
    built = _run_json(
        "backbone-cache",
        "build",
        "--limit",
        "30",
        cwd=tmp_path,
    )

    assert built["limit"] == 30
    assert built["prime_count"] == 10
    assert built["first_prime"] == 2
    assert built["last_prime"] == 29

    inspected = _run_json(
        "backbone-cache",
        "inspect",
        "--limit",
        "20",
        cwd=tmp_path,
    )

    assert inspected["cache_exists"] is True
    assert inspected["requested_limit"] == 20
    assert inspected["cache_limit"] == 30
    assert inspected["prime_count"] == 8
    assert inspected["first_prime"] == 2
    assert inspected["last_prime"] == 19


def test_cli_backbone_cache_inspect_reports_missing_cache(tmp_path):
    inspected = _run_json(
        "backbone-cache",
        "inspect",
        "--limit",
        "30",
        cwd=tmp_path,
    )

    assert inspected["cache_exists"] is False
    assert inspected["requested_limit"] == 30
    assert inspected["cache_path"] is None
    assert inspected["prime_count"] == 0

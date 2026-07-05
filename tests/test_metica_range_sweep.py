#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SWEEP = REPO_ROOT / "tools" / "research" / "pet_metica_range_sweep.py"


def _run(*extra: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SWEEP), *extra, "--json"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def test_metica_range_sweep_small_tiers_contract():
    data = _run(
        "--tier",
        "8:24",
        "--tier",
        "12:36",
        "--no-friction-tier",
        "--limit",
        "3",
    )

    assert "tiers" in data
    assert len(data["tiers"]) == 2
    assert data["friction_extended"] is None

    for tier in data["tiers"]:
        assert {"n_max", "overscan", "stats", "top_hubs", "family_report"} <= set(
            tier.keys()
        )
        assert len(tier["top_hubs"]) <= 3

    comparison = data["comparison"]
    assert "asymmetry_evolution" in comparison
    assert len(comparison["asymmetry_evolution"]) == 2


def test_metica_range_sweep_writes_report_files(tmp_path):
    json_path = tmp_path / "sweep.json"
    md_path = tmp_path / "sweep.md"

    subprocess.run(
        [
            sys.executable,
            str(SWEEP),
            "--tier",
            "6:18",
            "--no-friction-tier",
            "--limit",
            "2",
            "--output-json",
            str(json_path),
            "--output-md",
            str(md_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    assert json_path.exists()
    assert md_path.exists()

    md = md_path.read_text(encoding="utf-8")
    assert "## Scope" in md
    assert "## Observations" in md
    assert "## Interpretation and limits" in md
    assert "pet_metica_range_sweep.py" in md

#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE = REPO_ROOT / "tools" / "research" / "pet_metica_seven_family_probe.py"


def test_seven_family_members_up_to_300():
    sys.path.insert(0, str(REPO_ROOT / "tools" / "research"))
    from pet_metica_seven_family_probe import seven_family_members

    members = seven_family_members(300)
    assert members["dyadic"] == [7, 14, 28, 56, 112, 224]
    assert members["triadic"] == [7, 21, 63, 189]
    assert members["all"] == [7, 14, 21, 28, 56, 63, 112, 189, 224]


def test_seven_family_probe_small_window_contract():
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE),
            "--n-max",
            "64",
            "--overscan",
            "300",
            "--min-abs-asymmetry",
            "4",
            "--partner-limit",
            "5",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    data = json.loads(result.stdout)

    assert data["n_max"] == 64
    assert 56 in data["family_members"]["dyadic"]
    assert "canonical_seed_asymmetries" in data
    assert any(row["target"] == 56 for row in data["canonical_seed_asymmetries"]["dyadic_seeds"])
    assert any(row["asymmetry"] == 8 for row in data["canonical_seed_asymmetries"]["dyadic_seeds"])


def test_seven_family_probe_writes_files(tmp_path):
    json_path = tmp_path / "probe.json"
    md_path = tmp_path / "probe.md"

    subprocess.run(
        [
            sys.executable,
            str(PROBE),
            "--n-max",
            "40",
            "--overscan",
            "120",
            "--output-json",
            str(json_path),
            "--output-md",
            str(md_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    assert json_path.exists()
    md = md_path.read_text(encoding="utf-8")
    assert "## Scope" in md
    assert "7·2^k" in md
    assert "pet_metica_seven_family_probe.py" in md

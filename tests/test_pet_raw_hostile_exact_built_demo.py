from __future__ import annotations

import json
import subprocess
import sys


def test_pet_raw_hostile_exact_built_demo_smoke(tmp_path):
    out_dir = tmp_path / "demo"

    proc = subprocess.run(
        [
            sys.executable,
            "tools/pet_raw_hostile_exact_built_demo.py",
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))

    assert summary["schema"] == "pet-raw-hostile-exact-built-demo-v1"
    assert summary["input_n"] == 11413
    assert summary["final_status"] == "built-exact-match"
    assert summary["payload_count"] == 1
    assert summary["candidate_count"] == 1
    assert summary["attempted_count"] == 1
    assert summary["built_count"] == 1
    assert summary["exact_match_count"] == 1
    assert summary["terminal_status"] == "built"
    assert summary["builder_readiness"] == "ready"
    assert summary["build_status"] == "built"
    assert summary["assembly_status"] == "assembled"
    assert summary["known_support"] == [101, 113]

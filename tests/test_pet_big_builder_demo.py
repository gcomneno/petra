import json
import subprocess
import sys
from pathlib import Path


def test_pet_big_builder_demo_smoke(tmp_path):
    out_dir = tmp_path / "demo"

    proc = subprocess.run(
        [
            sys.executable,
            "tools/pet_big_builder_demo.py",
            "--prime-count",
            "8",
            "--exp",
            "2",
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))

    assert summary["schema"] == "pet-big-builder-demo-v1"
    assert summary["prime_count"] == 8
    assert summary["exponent"] == 2
    assert summary["first_prime"] == 2
    assert summary["last_prime"] == 19
    assert summary["steps"] == 15
    assert summary["path_len"] == 15
    assert summary["first_move"] == "INC(p=2,e=1)"
    assert summary["last_move"] == "INC(p=19,e=1)"
    assert summary["build_status"] == "built"
    assert summary["assembly_status"] == "assembled"
    assert summary["component_count"] == 8
    assert (out_dir / "factor_spec.json").exists()
    assert (out_dir / "artifacts").is_dir()

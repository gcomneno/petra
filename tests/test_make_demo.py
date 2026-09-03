import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_make_demo_uses_installed_cli_and_cleans_up(tmp_path):
    make = shutil.which("make")
    assert make is not None

    demo_tmp = tmp_path / "demo-tmp"
    demo_tmp.mkdir()
    env = os.environ.copy()
    env["PATH"] = os.defpath
    env["TMPDIR"] = str(demo_tmp)

    result = subprocess.run(
        [make, "demo", f"PYTHON={sys.executable}"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    expected = (
        "PETRA canonical CLI demo\n"
        "\n"
        "shape = 1\n"
        'invocation = {"schema":"petra.operator-invocation.v1",'
        '"operator":"SPROUT","target":{"mode":"default"}}\n'
        "\n"
        '{"address_effects":{"target_address":"@/","witness_address":"@/0"},'
        '"after_shape":"C(r0^1)","before_shape":"1",'
        '"invocation_target":{"mode":"default"},"operator":"SPROUT",'
        '"reason":"sprout-applied",'
        '"resolved_target":{"address":"@/","kind":"anchor"},'
        '"schema":"petra.operator-result.v1","status":"ok"}\n'
    )

    assert result.stdout == expected
    assert result.stderr == ""
    assert list(demo_tmp.iterdir()) == []

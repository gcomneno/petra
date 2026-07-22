import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap


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

    expected = textwrap.dedent(
        """\
        PET-Base demo (N=72)

        1. Encode canonical JSON
        [
          {
            "p": 2,
            "e": [
              {
                "p": 3,
                "e": null
              }
            ]
          },
          {
            "p": 3,
            "e": [
              {
                "p": 2,
                "e": null
              }
            ]
          }
        ]

        2. Show canonical metrics
        N = 72
        node_count = 4
        leaf_count = 2
        height = 2
        max_branching = 2
        branch_profile = [2, 2]
        recursive_mass = 2
        average_leaf_depth = 2.0
        leaf_depth_variance = 0.0

        3. Validate encoded artifact
        OK

        4. Decode encoded artifact
        72

        5. Assert roundtrip
        OK: decoded value matches original N=72
        """
    )

    assert result.stdout == expected
    assert result.stderr == ""
    assert list(demo_tmp.iterdir()) == []

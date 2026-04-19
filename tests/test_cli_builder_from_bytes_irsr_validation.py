import subprocess
import sys


def test_cli_builder_from_bytes_rejects_composite_irsr_seed_candidate(tmp_path):
    path = tmp_path / "n.bin"
    path.write_bytes((1000000007 * 1000000009).to_bytes(8, "big"))

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "builder-from-bytes",
            str(path),
            "--mode",
            "irsr",
            "--irsr-slot-candidates",
            "a=1000000007",
            "--irsr-slot-candidates",
            "b=1000000009,15",
            "--json",
        ],
        text=True,
        capture_output=True,
    )

    assert proc.returncode != 0
    assert "prime" in proc.stderr.lower()

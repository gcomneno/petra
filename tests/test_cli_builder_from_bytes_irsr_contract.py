import json
from pathlib import Path

from pet.cli import main as cli_main


def _write_int_bytes(path: Path, n: int) -> Path:
    path.write_bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))
    return path


def test_builder_from_bytes_irsr_builds_squarefree_profile(tmp_path: Path, capsys) -> None:
    n = 101 * 103 * 107
    input_file = _write_int_bytes(tmp_path / "squarefree-k3.bin", n)
    artifacts_dir = tmp_path / "artifacts-squarefree-k3"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["terminal_state"]["build_status"] == "built"
    assert payload["terminal_state"]["assembly_status"] == "assembled"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [1, 1, 1]


def test_builder_from_bytes_irsr_builds_prime_square_profile(tmp_path: Path, capsys) -> None:
    n = 101**2
    input_file = _write_int_bytes(tmp_path / "prime-square.bin", n)
    artifacts_dir = tmp_path / "artifacts-prime-square"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [2]


def test_builder_from_bytes_irsr_builds_square_times_prime_profile(tmp_path: Path, capsys) -> None:
    n = 101**2 * 103
    input_file = _write_int_bytes(tmp_path / "square-times-prime.bin", n)
    artifacts_dir = tmp_path / "artifacts-square-times-prime"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [2, 1]


def test_builder_from_bytes_irsr_reports_blocked_for_unsupported_profile(tmp_path: Path, capsys) -> None:
    n = 101**3
    input_file = _write_int_bytes(tmp_path / "unsupported-cube.bin", n)
    artifacts_dir = tmp_path / "artifacts-unsupported-cube"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "blocked"
    assert payload["builder_report"] is None
    assert payload["terminal_state"]["terminal_status"] == "blocked"


def test_builder_from_bytes_irsr_builds_medium_square_times_prime_profile(
    tmp_path: Path,
    capsys,
) -> None:
    n = 100003**2 * 100019
    input_file = _write_int_bytes(tmp_path / "medium-square-times-prime.bin", n)
    artifacts_dir = tmp_path / "artifacts-medium-square-times-prime"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [2, 1]


def test_builder_from_bytes_irsr_structural_radius_override_builds_large_square_times_prime(
    tmp_path: Path,
    capsys,
) -> None:
    n = 10000019**2 * 10000079
    input_file = _write_int_bytes(tmp_path / "large-square-times-prime.bin", n)
    artifacts_dir = tmp_path / "artifacts-large-square-times-prime"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--irsr-structural-radius",
            "64",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [2, 1]


def test_builder_from_bytes_irsr_structural_radius_override_builds_square_times_two_primes(
    tmp_path: Path,
    capsys,
) -> None:
    n = 100003**2 * 100019 * 100043
    input_file = _write_int_bytes(tmp_path / "square-times-two-primes.bin", n)
    artifacts_dir = tmp_path / "artifacts-square-times-two-primes"

    rc = cli_main(
        [
            "pet",
            "builder-from-bytes",
            str(input_file),
            "--mode",
            "irsr",
            "--irsr-structural-radius",
            "64",
            "--artifacts-dir",
            str(artifacts_dir),
            "--json",
        ]
    )

    assert rc in (0, None)
    payload = json.loads(capsys.readouterr().out)

    assert payload["input_n"] == n
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["support_report"]["exponent_multiset"] == [2, 1, 1]

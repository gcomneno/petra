import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_branch_neighbors_human_order_for_12():
    out = _run_cli("branch-neighbors", "12")
    assert "N = 12" in out
    assert "count = 5" in out

    lines = [line.strip() for line in out.splitlines() if line.strip().startswith("12 --")]
    assert lines == [
        "12 --NEW(p=5)--> 60",
        "12 --DROP(p=3)--> 4",
        "12 --INC(p=2,e=2)--> 24",
        "12 --INC(p=3,e=1)--> 36",
        "12 --DEC(p=2,e=2)--> 6",
    ]


def test_cli_branch_neighbors_json_order_for_12():
    payload = json.loads(_run_cli("branch-neighbors", "12", "--json"))
    assert payload["n"] == 12
    assert payload["count"] == 5
    assert [(row["kind"], row["label"], row["target_n"]) for row in payload["path"]] == [
        ("NEW", "NEW(p=5)", 60),
        ("DROP", "DROP(p=3)", 4),
        ("INC", "INC(p=2,e=2)", 24),
        ("INC", "INC(p=3,e=1)", 36),
        ("DEC", "DEC(p=2,e=2)", 6),
    ]


def test_cli_branch_neighbors_is_deterministic():
    args = ("branch-neighbors", "12")
    outs = [_run_cli(*args) for _ in range(4)]
    assert all(out == outs[0] for out in outs[1:])

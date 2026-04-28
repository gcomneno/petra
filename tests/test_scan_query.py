#!/usr/bin/env python3
import json
import subprocess
import sys


def test_scan_query_filter_height_and_branching(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "30",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "tools/scan_query.py",
            "filter",
            str(jsonl_path),
            "--where",
            "height=2",
            "--where",
            "max_branching>=2",
            "--limit",
            "5",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [12, 18, 20, 24, 28]
    assert all(row["schema_version"] == 2 for row in rows)


def test_scan_query_group_count_branch_profile(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "12",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "tools/scan_query.py",
            "group-count",
            str(jsonl_path),
            "--field",
            "branch_profile",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = """[1]\t5
[1, 1]\t3
[2]\t2
[2, 1]\t1
"""
    assert "\n".join(" ".join(line.split()) for line in result.stdout.strip().splitlines()) == \
        "\n".join(" ".join(line.split()) for line in expected.strip().splitlines())


def test_scan_query_filter_leaf_depth_variance_float(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "100",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "tools/scan_query.py",
            "filter",
            str(jsonl_path),
            "--where",
            "leaf_depth_variance=1.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["n"] for row in rows] == [48, 80]


def test_scan_query_rejects_branch_profile_ordering_operator(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "30",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "tools/scan_query.py",
            "filter",
            str(jsonl_path),
            "--where",
            "branch_profile>=[2,1]",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "branch_profile only supports '='" in result.stderr

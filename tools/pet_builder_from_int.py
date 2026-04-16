#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _run_json(cmd: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON from command {cmd!r}: {exc}")


def _build_from_int_pipeline(n: int, output_dir: str) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = src_path + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    cli_cmd = [
        sys.executable,
        "-m",
        "pet.cli",
        "build-from-int",
        str(n),
        "--allow-non-canonical-support",
        "--json",
    ]

    support_tool = str(repo_root / "tools" / "pet_support_realization.py")
    plan_tool = str(repo_root / "tools" / "pet_builder_plan.py")
    execute_tool = str(repo_root / "tools" / "pet_builder_execute.py")

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        cli_payload = _run_json(cli_cmd, env=env)
        cli_path = td_path / "cli.json"
        cli_path.write_text(json.dumps(cli_payload), encoding="utf-8")

        support_report = _run_json(
            [sys.executable, support_tool, "--json", str(cli_path)],
            env=env,
        )
        support_path = td_path / "support.json"
        support_path.write_text(json.dumps(support_report), encoding="utf-8")

        builder_plan = _run_json(
            [sys.executable, plan_tool, str(support_path)],
            env=env,
        )
        plan_path = td_path / "plan.json"
        plan_path.write_text(json.dumps(builder_plan), encoding="utf-8")

        builder_execution = _run_json(
            [
                sys.executable,
                execute_tool,
                str(plan_path),
                "--output-dir",
                output_dir,
            ],
            env=env,
        )

    return {
        "schema": "pet-builder-from-int-v0",
        "input_n": n,
        "cli_payload": cli_payload,
        "support_report": support_report,
        "builder_plan": builder_plan,
        "builder_execution": builder_execution,
        "final_build_output": builder_execution.get("final_build_output"),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run the PET builder pipeline from an integer input.",
    )
    parser.add_argument("n", type=int, help="target integer")
    parser.add_argument(
        "--output-dir",
        default="/tmp/pet_builder_from_int_out",
        help="directory for materialized builder artifacts",
    )
    args = parser.parse_args(argv[1:])

    report = _build_from_int_pipeline(args.n, args.output_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

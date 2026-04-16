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


def build_cli_payload_from_factors_file(file: str | Path) -> dict[str, Any]:
    from pet.cli import _build_from_factors_report, _parse_factor_spec_file

    factors = _parse_factor_spec_file(str(file))
    report = _build_from_factors_report(factors)

    return {
        "input_n": report["target_n"],
        "start_n": report["start_n"],
        "factors": tuple(report["factors"]),
        "target_n": report["target_n"],
        "target_generator": report["target_generator"],
        "steps": report["steps"],
        "path": report["path"],
    }


def build_from_factors_pipeline(file: str | Path, output_dir: str | Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = src_path + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    support_tool = str(repo_root / "tools" / "pet_support_realization.py")
    plan_tool = str(repo_root / "tools" / "pet_builder_plan.py")
    execute_tool = str(repo_root / "tools" / "pet_builder_execute.py")

    cli_payload = build_cli_payload_from_factors_file(file)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

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
                str(output_dir),
            ],
            env=env,
        )

    return {
        "schema": "pet-builder-from-factors-v0",
        "factor_spec_file": str(file),
        "input_n": cli_payload["input_n"],
        "cli_payload": cli_payload,
        "support_report": support_report,
        "builder_plan": builder_plan,
        "builder_execution": builder_execution,
        "final_build_output": builder_execution.get("final_build_output"),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run the PET builder pipeline from a factor specification file.",
    )
    parser.add_argument("file", metavar="FACTORS.json")
    parser.add_argument(
        "--output-dir",
        default="/tmp/pet_builder_from_factors_out",
        help="directory for materialized builder artifacts",
    )
    args = parser.parse_args(argv[1:])

    report = build_from_factors_pipeline(args.file, args.output_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

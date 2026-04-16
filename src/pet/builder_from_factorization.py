from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pet.core import is_prime, shape_signature_dict


def _run_json(cmd: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON from command {cmd!r}: {exc}")


def _parse_noncanonical_factor_spec_file(path_str: str) -> tuple[tuple[int, int], ...]:
    payload = json.loads(Path(path_str).read_text(encoding="utf-8"))

    if isinstance(payload, dict):
        if "factors" not in payload:
            raise ValueError("factor spec dict must contain a 'factors' key")
        payload = payload["factors"]

    if not isinstance(payload, list):
        raise ValueError("factor spec must be a JSON list or an object with a 'factors' list")

    factors: list[tuple[int, int]] = []
    seen: set[int] = set()

    for row in payload:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError("each factor row must be a pair [prime, exponent]")

        prime, exp = row
        if not isinstance(prime, int) or not isinstance(exp, int):
            raise ValueError("prime and exponent must be integers")
        if prime < 2:
            raise ValueError("prime must be >= 2")
        if exp < 1:
            raise ValueError("exponent must be >= 1")
        if not is_prime(prime):
            raise ValueError(f"{prime} is not prime")
        if prime in seen:
            raise ValueError(f"duplicate prime in factor spec: {prime}")

        seen.add(prime)
        factors.append((prime, exp))

    factors.sort()

    if not factors:
        raise ValueError("factor spec cannot be empty")

    return tuple(factors)


def build_cli_payload_from_factorization_file(file: str | Path) -> dict[str, Any]:
    factors = _parse_noncanonical_factor_spec_file(str(file))

    input_n = 1
    for prime, exp in factors:
        input_n *= prime ** exp

    sig = shape_signature_dict(input_n)

    return {
        "schema": "pet-support-realization-input-v0",
        "input_n": input_n,
        "target_generator": sig["generator"],
        "shape_signature": sig["signature"],
        "slot_count": len(factors),
        "exponent_multiset": sorted((exp for _prime, exp in factors), reverse=True),
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": f"p{prime}-exp{exp}",
                "slot_exp": exp,
                "slot_multiplicity": 1,
                "target_product": prime,
                "constraints": {
                    "prime_only": True,
                    "count": 1,
                    "derived_from_known_factors": True,
                },
            }
            for prime, exp in factors
        ],
        "unknown_blocks": [],
    }


def build_from_factorization_pipeline(file: str | Path, output_dir: str | Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = src_path + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    support_tool = str(repo_root / "tools" / "pet_support_realization.py")
    plan_tool = str(repo_root / "tools" / "pet_builder_plan.py")
    execute_tool = str(repo_root / "tools" / "pet_builder_execute.py")

    cli_payload = build_cli_payload_from_factorization_file(file)

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
        "schema": "pet-builder-from-factorization-v0",
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
        description="Run the PET builder pipeline from a known factorization file.",
    )
    parser.add_argument("file", metavar="FACTORS.json")
    parser.add_argument(
        "--output-dir",
        default="/tmp/pet_builder_from_factorization_out",
        help="directory for materialized builder artifacts",
    )
    args = parser.parse_args(argv[1:])

    report = build_from_factorization_pipeline(args.file, args.output_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

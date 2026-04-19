from __future__ import annotations

import argparse
import json
from pathlib import Path

from pet.irsr_state import (
    run_hostile_semiprime_irsr_to_builder_results,
    try_seed_residual_state_slot_candidates,
)


def _seed_a_with_101(state: dict):
    return try_seed_residual_state_slot_candidates(state, "a", [101])


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def build_demo(output_dir: str | Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts_dir = output_dir / "artifacts"

    result = run_hostile_semiprime_irsr_to_builder_results(
        11413,
        max_steps=5,
        open_portfolios=[
            {
                "name": "tight-seeding",
                "priority": 100,
                "budget": 2,
                "refiners": [_seed_a_with_101, _seed_b_with_113],
            }
        ],
        branch_portfolios=[],
        output_dir=artifacts_dir,
    )

    terminal = result["terminal_state"]
    summary = {
        "schema": "pet-raw-hostile-exact-built-demo-v1",
        "input_n": 11413,
        "final_status": result["final_status"],
        "payload_count": result["payload_summary"]["payload_count"],
        "candidate_count": result["build_summary"]["candidate_count"],
        "attempted_count": result["build_summary"]["attempted_count"],
        "built_count": result["build_summary"]["built_count"],
        "exact_match_count": result["build_summary"]["exact_match_count"],
        "terminal_status": terminal["status"],
        "builder_readiness": terminal["builder_readiness"],
        "build_status": terminal.get("build_status"),
        "assembly_status": terminal.get("assembly_status"),
        "known_support": terminal["known_support"],
        "artifacts_dir": str(artifacts_dir),
        "summary_file": str(output_dir / "summary.json"),
    }

    (output_dir / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the raw hostile exact-built IRSR demo for n=11413.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/pet_raw_hostile_exact_built_demo",
        help="directory where summary/result/artifacts are written",
    )
    args = parser.parse_args()

    summary = build_demo(args.output_dir)

    for key in [
        "schema",
        "input_n",
        "final_status",
        "payload_count",
        "candidate_count",
        "attempted_count",
        "built_count",
        "exact_match_count",
        "terminal_status",
        "builder_readiness",
        "build_status",
        "assembly_status",
        "known_support",
        "artifacts_dir",
        "summary_file",
    ]:
        print(f"{key} = {summary[key]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

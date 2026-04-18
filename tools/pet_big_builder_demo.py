from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    sys.set_int_max_str_digits(0)
except AttributeError:
    pass

from pet.builder_from_factors import build_from_factors_pipeline
from pet.cli import _build_from_factors_report


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def first_primes(count: int) -> list[int]:
    if count < 1:
        raise ValueError("prime_count must be >= 1")

    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes


def build_factor_spec(prime_count: int, exp: int) -> tuple[tuple[int, int], ...]:
    if exp < 1:
        raise ValueError("exp must be >= 1")
    return tuple((prime, exp) for prime in first_primes(prime_count))


def _pick_field(*sources: dict, key: str):
    for source in sources:
        if isinstance(source, dict) and key in source and source[key] is not None:
            return source[key]
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a repeatable large-number PET demo from a known factor specification.",
    )
    parser.add_argument(
        "--prime-count",
        type=int,
        required=True,
        help="number of consecutive primes to include in the support",
    )
    parser.add_argument(
        "--exp",
        type=int,
        default=2,
        help="shared exponent for every support prime (default: 2)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="directory where demo inputs, summary, and artifacts will be written",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    factors = build_factor_spec(args.prime_count, args.exp)
    factor_spec_path = output_dir / "factor_spec.json"
    factor_spec_path.write_text(
        json.dumps({"factors": [[p, e] for p, e in factors]}, indent=2),
        encoding="utf-8",
    )

    report = _build_from_factors_report(factors)
    pipeline = build_from_factors_pipeline(
        factor_spec_path,
        output_dir / "artifacts",
    )

    builder_execution = pipeline.get("builder_execution", {})
    final_build_output = pipeline.get("final_build_output", {})
    built_pet_object = final_build_output.get("built_pet_object", {}) if isinstance(final_build_output, dict) else {}

    summary = {
        "schema": "pet-big-builder-demo-v1",
        "prime_count": args.prime_count,
        "exponent": args.exp,
        "first_prime": factors[0][0],
        "last_prime": factors[-1][0],
        "factor_spec_file": str(factor_spec_path),
        "target_digits": len(str(report["target_n"])),
        "target_generator_digits": len(str(report["target_generator"])),
        "steps": report["steps"],
        "path_len": len(report["path"]),
        "first_move": None if not report["path"] else report["path"][0]["label"],
        "last_move": None if not report["path"] else report["path"][-1]["label"],
        "build_status": _pick_field(final_build_output, builder_execution, key="build_status"),
        "assembly_status": _pick_field(built_pet_object, final_build_output, builder_execution, key="assembly_status"),
        "component_count": _pick_field(built_pet_object, final_build_output, builder_execution, key="component_count"),
        "artifacts_dir": str(output_dir / "artifacts"),
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"schema = {summary['schema']}")
    print(f"prime_count = {summary['prime_count']}")
    print(f"exponent = {summary['exponent']}")
    print(f"first_prime = {summary['first_prime']}")
    print(f"last_prime = {summary['last_prime']}")
    print(f"target_digits = {summary['target_digits']}")
    print(f"target_generator_digits = {summary['target_generator_digits']}")
    print(f"steps = {summary['steps']}")
    print(f"path_len = {summary['path_len']}")
    print(f"first_move = {summary['first_move']}")
    print(f"last_move = {summary['last_move']}")
    print(f"build_status = {summary['build_status']}")
    print(f"assembly_status = {summary['assembly_status']}")
    print(f"component_count = {summary['component_count']}")
    print(f"factor_spec_file = {summary['factor_spec_file']}")
    print(f"artifacts_dir = {summary['artifacts_dir']}")
    print(f"summary_file = {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

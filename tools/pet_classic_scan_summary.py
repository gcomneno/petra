#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class VerifiedDivisor:
    divisor: int
    cofactor: int
    sources: set[str]


def run_command(args: list[str]) -> tuple[str, str | None]:
    result = subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return "", result.stderr.strip() or "command failed"
    return result.stdout, None


def extract_value(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def parse_verified_divisors(text: str) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    current_divisor: int | None = None

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("divisor_found = "):
            raw = stripped.removeprefix("divisor_found = ")
            if raw == "none":
                current_divisor = None
                continue
            current_divisor = int(raw)
            continue

        if stripped.startswith("cofactor = ") and current_divisor is not None:
            raw = stripped.removeprefix("cofactor = ")
            if raw != "none":
                found.append((current_divisor, int(raw)))
            current_divisor = None

    return found


def generator_for(n: int) -> str:
    output, error = run_command([sys.executable, "-m", "pet.cli", "generator", str(n)])
    if error:
        return "unknown"
    return output.strip()


def role_hint(divisor_generator: str, cofactor_generator: str) -> str:
    if divisor_generator == "2" and cofactor_generator == "2":
        return "prime-like split"
    if divisor_generator == "2":
        return "single-leaf divisor"
    if cofactor_generator == "2":
        return "composite-block isolates single-leaf cofactor"
    if divisor_generator == cofactor_generator:
        return "balanced structural split"
    return "verified structural divisor"


def add_results(
    results: dict[int, VerifiedDivisor],
    source: str,
    pairs: list[tuple[int, int]],
) -> None:
    for divisor, cofactor in pairs:
        record = results.setdefault(
            divisor,
            VerifiedDivisor(divisor=divisor, cofactor=cofactor, sources=set()),
        )
        record.sources.add(source)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize PET-guided classic scan verified divisors."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--fixed-radius", type=int, default=500)
    parser.add_argument("--radius-digits", type=int, default=5)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_classic_scan_summary expects integers >= 1")

    results: dict[int, VerifiedDivisor] = {}
    source_errors: dict[str, str] = {}

    crumb, error = run_command([sys.executable, "tools/pet_crumb_classic_scan.py", str(args.n)])
    if error:
        source_errors["crumb"] = error
    else:
        add_results(results, "crumb", parse_verified_divisors(crumb))

    fixed_source = f"root-window-fixed:{args.fixed_radius}"
    root_fixed, error = run_command(
        [
            sys.executable,
            "tools/pet_root_window_classic_scan.py",
            str(args.n),
            "--radius",
            str(args.fixed_radius),
        ]
    )
    if error:
        source_errors[fixed_source] = error
    else:
        add_results(results, fixed_source, parse_verified_divisors(root_fixed))

    digits_source = f"root-window-digits:{args.radius_digits}"
    root_digits, error = run_command(
        [
            sys.executable,
            "tools/pet_root_window_classic_scan.py",
            str(args.n),
            "--radius-digits",
            str(args.radius_digits),
        ]
    )
    if error:
        source_errors[digits_source] = error
    else:
        add_results(results, digits_source, parse_verified_divisors(root_digits))

    print("PET CLASSIC SCAN SUMMARY")
    print()
    print(f"N = {args.n}")
    print(f"fixed_radius = {args.fixed_radius}")
    print(f"radius_digits = {args.radius_digits}")
    print()

    for source, error in sorted(source_errors.items()):
        print(f"source_status {source} = unavailable")
        print(f"source_reason {source} = {error}")

    if source_errors:
        print()

    if not results:
        print("verified_divisor = none")
        print()
        print("claim = PET-guided classic scan summary only; divisors are accepted only when verified")
        return 0

    for divisor in sorted(results):
        record = results[divisor]
        divisor_generator = generator_for(record.divisor)
        cofactor_generator = generator_for(record.cofactor)

        print(f"verified_divisor = {record.divisor}")
        print(f"cofactor = {record.cofactor}")
        print(f"sources = {','.join(sorted(record.sources))}")
        print(f"divisor_generator = {divisor_generator}")
        print(f"cofactor_generator = {cofactor_generator}")
        print(f"role_hint = {role_hint(divisor_generator, cofactor_generator)}")
        print()

    print(f"verified_divisor_count = {len(results)}")
    print()
    print("claim = PET-guided classic scan summary only; divisors are accepted only when verified")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

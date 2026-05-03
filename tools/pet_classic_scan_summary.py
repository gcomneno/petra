#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from math import isqrt


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


def parse_json_verified_divisors(text: str) -> list[tuple[int, int]]:
    payload = json.loads(text)
    found: list[tuple[int, int]] = []

    if payload.get("verified", False):
        divisor = payload.get("divisor_found")
        cofactor = payload.get("cofactor")
        if divisor is not None and cofactor is not None:
            found.append((int(divisor), int(cofactor)))

    for record in payload.get("verified_divisors", []):
        if not record.get("verified", False):
            continue

        divisor = record.get("divisor")
        cofactor = record.get("cofactor")
        if divisor is None or cofactor is None:
            continue

        found.append((int(divisor), int(cofactor)))

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


def digit_radius_scope(n: int, radius_digits: int) -> str:
    radius = 10 ** radius_digits
    if radius >= isqrt(n):
        return "exhaustive-like"
    return "bounded-window"


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


def source_detail(source: str) -> dict[str, object]:
    if source == "crumb":
        return {
            "source": source,
            "kind": "crumb",
            "scope": "baseline",
        }

    if source.startswith("root-window-fixed:"):
        _, raw_radius = source.rsplit(":", maxsplit=1)
        return {
            "source": source,
            "kind": "root-window-fixed",
            "radius": int(raw_radius),
            "scope": "bounded-window",
        }

    if source.startswith("root-window-digits:"):
        parts = source.split(":")
        if len(parts) == 3:
            return {
                "source": source,
                "kind": "root-window-digits",
                "radius_digits": int(parts[1]),
                "scope": parts[2],
            }

    return {
        "source": source,
        "kind": "unknown",
        "scope": "unknown",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize PET-guided classic scan verified divisors."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--fixed-radius", type=int, default=500)
    parser.add_argument("--radius-digits", type=int, default=5)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_classic_scan_summary expects integers >= 1")

    results: dict[int, VerifiedDivisor] = {}
    source_errors: dict[str, str] = {}

    crumb, error = run_command(
        [sys.executable, "tools/pet_crumb_classic_scan.py", str(args.n), "--json"]
    )
    if error:
        source_errors["crumb"] = error
    else:
        add_results(results, "crumb", parse_json_verified_divisors(crumb))

    fixed_source = f"root-window-fixed:{args.fixed_radius}"
    root_fixed, error = run_command(
        [
            sys.executable,
            "tools/pet_root_window_classic_scan.py",
            str(args.n),
            "--radius",
            str(args.fixed_radius),
            "--json",
        ]
    )
    if error:
        source_errors[fixed_source] = error
    else:
        add_results(results, fixed_source, parse_json_verified_divisors(root_fixed))

    digits_scope = digit_radius_scope(args.n, args.radius_digits)
    digits_source = f"root-window-digits:{args.radius_digits}:{digits_scope}"
    root_digits, error = run_command(
        [
            sys.executable,
            "tools/pet_root_window_classic_scan.py",
            str(args.n),
            "--radius-digits",
            str(args.radius_digits),
            "--json",
        ]
    )
    if error:
        source_errors[digits_source] = error
    else:
        add_results(results, digits_source, parse_json_verified_divisors(root_digits))

    claim = "PET-guided classic scan summary only; divisors are accepted only when verified"
    digit_scope = digit_radius_scope(args.n, args.radius_digits)

    verified_divisors = []
    for divisor in sorted(results):
        record = results[divisor]
        divisor_generator = generator_for(record.divisor)
        cofactor_generator = generator_for(record.cofactor)
        verified_divisors.append(
            {
                "divisor": record.divisor,
                "cofactor": record.cofactor,
                "sources": sorted(record.sources),
                "source_details": [
                    source_detail(source)
                    for source in sorted(record.sources)
                ],
                "divisor_generator": divisor_generator,
                "cofactor_generator": cofactor_generator,
                "role_hint": role_hint(divisor_generator, cofactor_generator),
                "verified": True,
            }
        )

    payload = {
        "n": args.n,
        "fixed_radius": args.fixed_radius,
        "radius_digits": args.radius_digits,
        "root_window_digit_scope": digit_scope,
        "source_errors": {
            source: error for source, error in sorted(source_errors.items())
        },
        "verified_divisors": verified_divisors,
        "verified_divisor_count": len(verified_divisors),
        "claim": claim,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("PET CLASSIC SCAN SUMMARY")
    print()
    print(f"N = {args.n}")
    print(f"fixed_radius = {args.fixed_radius}")
    print(f"radius_digits = {args.radius_digits}")
    print(f"root_window_digit_scope = {digit_scope}")
    print()

    for source, error in sorted(source_errors.items()):
        print(f"source_status {source} = unavailable")
        print(f"source_reason {source} = {error}")

    if source_errors:
        print()

    if not verified_divisors:
        print("verified_divisor = none")
        print()
        print(f"claim = {claim}")
        return 0

    for record in verified_divisors:
        print(f"verified_divisor = {record['divisor']}")
        print(f"cofactor = {record['cofactor']}")
        print(f"sources = {','.join(record['sources'])}")
        print(f"divisor_generator = {record['divisor_generator']}")
        print(f"cofactor_generator = {record['cofactor_generator']}")
        print(f"role_hint = {record['role_hint']}")
        print()

    print(f"verified_divisor_count = {len(verified_divisors)}")
    print()
    print(f"claim = {claim}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

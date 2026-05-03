#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


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


def classify_source(source: str, source_errors: dict[str, str]) -> dict[str, Any]:
    if source in source_errors:
        return {
            "source": source,
            "status": "unavailable",
            "source_kind": "unavailable",
            "usable": False,
            "reason": source_errors[source],
        }

    if source == "crumb":
        return {
            "source": source,
            "status": "available",
            "source_kind": "baseline",
            "usable": True,
            "reason": "first-step classic fallback",
        }

    if source.endswith(":exhaustive-like"):
        return {
            "source": source,
            "status": "available",
            "source_kind": "exhaustive-like",
            "usable": False,
            "reason": "digit radius reaches exhaustive-like low-side coverage",
        }

    if source.endswith(":bounded-window") or source.startswith("root-window-fixed:"):
        return {
            "source": source,
            "status": "available",
            "source_kind": "bounded-window",
            "usable": True,
            "reason": "bounded root-window classic scan",
        }

    return {
        "source": source,
        "status": "available",
        "source_kind": "unknown",
        "usable": False,
        "reason": "unrecognized scan source policy",
    }


def classify_source_detail(
    detail: dict[str, Any],
    source_errors: dict[str, str],
) -> dict[str, Any]:
    source = str(detail.get("source", "unknown"))
    if source in source_errors:
        return {
            "source": source,
            "status": "unavailable",
            "source_kind": "unavailable",
            "usable": False,
            "reason": source_errors[source],
        }

    kind = detail.get("kind")
    scope = detail.get("scope")

    if kind == "crumb":
        return {
            "source": source,
            "status": "available",
            "source_kind": "baseline",
            "usable": True,
            "reason": "first-step classic fallback",
        }

    if kind == "root-window-digits" and scope == "exhaustive-like":
        return {
            "source": source,
            "status": "available",
            "source_kind": "exhaustive-like",
            "usable": False,
            "reason": "digit radius reaches exhaustive-like low-side coverage",
        }

    if kind in {"root-window-fixed", "root-window-digits"} and scope == "bounded-window":
        return {
            "source": source,
            "status": "available",
            "source_kind": "bounded-window",
            "usable": True,
            "reason": "bounded root-window classic scan",
        }

    return classify_source(source, source_errors)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify PET classic scan summary sources by operational policy."
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
        raise SystemExit("pet_classic_scan_policy expects integers >= 1")

    summary_text, error = run_command(
        [
            sys.executable,
            "tools/pet_classic_scan_summary.py",
            str(args.n),
            "--fixed-radius",
            str(args.fixed_radius),
            "--radius-digits",
            str(args.radius_digits),
            "--json",
        ]
    )
    if error:
        raise SystemExit(error)

    summary = json.loads(summary_text)
    source_errors = summary.get("source_errors", {})

    discovered_details: dict[str, dict[str, Any]] = {}
    discovered_sources = set(source_errors)

    for record in summary.get("verified_divisors", []):
        for detail in record.get("source_details", []):
            source = str(detail.get("source", "unknown"))
            discovered_details[source] = detail
            discovered_sources.add(source)

        for source in record.get("sources", []):
            discovered_sources.add(source)

    source_policies = []
    for source in sorted(discovered_sources):
        if source in discovered_details:
            source_policies.append(
                classify_source_detail(discovered_details[source], source_errors)
            )
        else:
            source_policies.append(classify_source(source, source_errors))

    usable_sources = [
        policy["source"]
        for policy in source_policies
        if policy["usable"]
    ]
    baseline_sources = [
        policy["source"]
        for policy in source_policies
        if policy["source_kind"] == "baseline"
    ]
    recommended_sources = [
        policy["source"]
        for policy in source_policies
        if policy["source_kind"] == "bounded-window"
    ]
    caution_sources = [
        policy["source"]
        for policy in source_policies
        if policy["source_kind"] == "exhaustive-like"
    ]
    unavailable_sources = [
        policy["source"]
        for policy in source_policies
        if policy["status"] == "unavailable"
    ]

    payload = {
        "n": args.n,
        "fixed_radius": args.fixed_radius,
        "radius_digits": args.radius_digits,
        "root_window_digit_scope": summary.get("root_window_digit_scope"),
        "source_policies": source_policies,
        "usable_sources": usable_sources,
        "baseline_sources": baseline_sources,
        "recommended_sources": recommended_sources,
        "caution_sources": caution_sources,
        "unavailable_sources": unavailable_sources,
        "verified_divisor_count": summary.get("verified_divisor_count", 0),
        "claim": "PET classic scan policy only; it classifies scan sources and does not verify new divisors",
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("PET CLASSIC SCAN POLICY")
    print()
    print(f"N = {args.n}")
    print(f"fixed_radius = {args.fixed_radius}")
    print(f"radius_digits = {args.radius_digits}")
    print(f"root_window_digit_scope = {payload['root_window_digit_scope']}")
    print()

    for policy in source_policies:
        print(f"source = {policy['source']}")
        print(f"status = {policy['status']}")
        print(f"source_kind = {policy['source_kind']}")
        print(f"usable = {'yes' if policy['usable'] else 'no'}")
        print(f"reason = {policy['reason']}")
        print()

    print(f"usable_sources = {','.join(usable_sources) if usable_sources else 'none'}")
    print(f"baseline_sources = {','.join(baseline_sources) if baseline_sources else 'none'}")
    print(f"recommended_sources = {','.join(recommended_sources) if recommended_sources else 'none'}")
    print(f"caution_sources = {','.join(caution_sources) if caution_sources else 'none'}")
    print(f"unavailable_sources = {','.join(unavailable_sources) if unavailable_sources else 'none'}")
    print(f"verified_divisor_count = {payload['verified_divisor_count']}")
    print()
    print(f"claim = {payload['claim']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

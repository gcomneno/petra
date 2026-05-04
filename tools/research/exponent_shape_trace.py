#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet.core import shape_signature_dict


def exponent_info(e: int) -> dict:
    if e < 1:
        raise ValueError("exponent must be >= 1")

    if e == 1:
        return {
            "e": 1,
            "generator": 1,
            "signature": [],
        }

    data = shape_signature_dict(e)
    return {
        "e": e,
        "generator": data["generator"],
        "signature": data["signature"],
    }


def build_trace(start: int, limit: int) -> dict:
    if start < 1:
        raise ValueError("start must be >= 1")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if start > limit:
        raise ValueError("start must be <= limit")

    exponents = [exponent_info(e) for e in range(start, limit + 1)]

    transitions = []
    signature_changed_count = 0
    generator_changed_count = 0

    for i in range(len(exponents) - 1):
        before = exponents[i]
        after = exponents[i + 1]
        signature_changed = before["signature"] != after["signature"]
        generator_changed = before["generator"] != after["generator"]

        if signature_changed:
            signature_changed_count += 1
        if generator_changed:
            generator_changed_count += 1

        transitions.append(
            {
                "from_exp": before["e"],
                "to_exp": after["e"],
                "from_generator": before["generator"],
                "to_generator": after["generator"],
                "from_signature": before["signature"],
                "to_signature": after["signature"],
                "signature_changed": signature_changed,
                "generator_changed": generator_changed,
            }
        )

    transition_count = len(transitions)

    return {
        "start": start,
        "limit": limit,
        "summary": {
            "transition_count": transition_count,
            "signature_changed_count": signature_changed_count,
            "signature_unchanged_count": transition_count - signature_changed_count,
            "generator_changed_count": generator_changed_count,
            "generator_unchanged_count": transition_count - generator_changed_count,
        },
        "exponents": exponents,
        "transitions": transitions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit exponent PET shape trace for e = N1..N2."
    )
    parser.add_argument("n1", type=int, help="Start exponent, or maximum exponent if n2 is omitted")
    parser.add_argument("n2", type=int, nargs="?", help="Maximum exponent (optional)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        if args.n2 is None:
            start = 1
            limit = args.n1
        else:
            start = args.n1
            limit = args.n2

        report = build_trace(start, limit)

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"start = {report['start']}")
            print(f"limit = {report['limit']}")
            print(f"summary = {report['summary']}")
            print("exponents:")
            for item in report["exponents"]:
                print(
                    f"  e={item['e']} "
                    f"generator={item['generator']} "
                    f"signature={item['signature']}"
                )
            print("transitions:")
            for item in report["transitions"]:
                print(
                    f"  {item['from_exp']} -> {item['to_exp']} "
                    f"sig_changed={item['signature_changed']} "
                    f"gen_changed={item['generator_changed']} "
                    f"{item['from_signature']} -> {item['to_signature']}"
                )

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

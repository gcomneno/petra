#!/usr/bin/env python3
"""Research-only PET/PEG Z-axis route/history reference probe.

This probe validates the history-prefix-level interpretation:

    REDIRECT(at_history_prefix, from_next, to_next)
    SHADOW_SELECT(at_history_prefix, selected_next)

It works on synthetic path-history labels. It does not execute routes, mutate
PET objects, change stable routing behavior, change residual descent, change
anchor selection, or make factorization claims.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "pet.operator_z_route_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 Z-axis history-prefix route reference probe; "
    "no stable routing/operator behavior change"
)


def parse_string_list(raw: str, field: str) -> list[str]:
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError(f"{field} must be a JSON list")

    values: list[str] = []
    for item in data:
        if not isinstance(item, str):
            raise ValueError(f"{field} entries must be strings")
        if not item:
            raise ValueError(f"{field} entries must be non-empty strings")
        values.append(item)

    return values


def prefix_status(history: list[str], prefix: list[str]) -> dict[str, Any]:
    if len(prefix) > len(history):
        return {
            "valid": False,
            "reason": "prefix-longer-than-history",
            "next_index": None,
            "expected_next": None,
        }

    expected_slice = history[: len(prefix)]
    if prefix != expected_slice:
        return {
            "valid": False,
            "reason": "prefix-does-not-match-history",
            "next_index": None,
            "expected_next": None,
            "expected_prefix": expected_slice,
        }

    next_index = len(prefix)
    expected_next = history[next_index] if next_index < len(history) else None

    return {
        "valid": True,
        "reason": None,
        "next_index": next_index,
        "expected_next": expected_next,
    }


def classify_redirect(
    history: list[str],
    prefix: list[str],
    candidates: list[str],
    from_next: str,
    to_next: str,
) -> dict[str, Any]:
    prefix_result = prefix_status(history, prefix)

    if not prefix_result["valid"]:
        return {
            "op": "REDIRECT",
            "valid": False,
            "reason": "invalid-history-prefix",
            "prefix_reason": prefix_result["reason"],
            "prefix": prefix,
            "from_next": from_next,
            "to_next": to_next,
        }

    expected_next = prefix_result["expected_next"]
    if expected_next is None:
        return {
            "op": "REDIRECT",
            "valid": False,
            "reason": "prefix-at-history-end",
            "prefix": prefix,
            "from_next": from_next,
            "to_next": to_next,
        }

    if from_next != expected_next:
        return {
            "op": "REDIRECT",
            "valid": False,
            "reason": "from-next-does-not-match-history-next",
            "expected_next": expected_next,
            "prefix": prefix,
            "from_next": from_next,
            "to_next": to_next,
        }

    if to_next not in candidates:
        return {
            "op": "REDIRECT",
            "valid": False,
            "reason": "to-next-not-in-candidate-set",
            "expected_next": expected_next,
            "candidates": candidates,
            "prefix": prefix,
            "from_next": from_next,
            "to_next": to_next,
        }

    if to_next == from_next:
        return {
            "op": "REDIRECT",
            "valid": False,
            "reason": "redirect-target-equals-source",
            "expected_next": expected_next,
            "candidates": candidates,
            "prefix": prefix,
            "from_next": from_next,
            "to_next": to_next,
        }

    return {
        "op": "REDIRECT",
        "valid": True,
        "reason": None,
        "prefix": prefix,
        "next_index": prefix_result["next_index"],
        "from_next": from_next,
        "to_next": to_next,
        "candidates": candidates,
    }


def classify_shadow_select(
    history: list[str],
    prefix: list[str],
    candidates: list[str],
    selected_next: str,
) -> dict[str, Any]:
    prefix_result = prefix_status(history, prefix)

    if not prefix_result["valid"]:
        return {
            "op": "SHADOW_SELECT",
            "valid": False,
            "reason": "invalid-history-prefix",
            "prefix_reason": prefix_result["reason"],
            "prefix": prefix,
            "selected_next": selected_next,
        }

    if selected_next not in candidates:
        return {
            "op": "SHADOW_SELECT",
            "valid": False,
            "reason": "selected-next-not-in-candidate-set",
            "candidates": candidates,
            "prefix": prefix,
            "selected_next": selected_next,
        }

    return {
        "op": "SHADOW_SELECT",
        "valid": True,
        "reason": None,
        "prefix": prefix,
        "next_index": prefix_result["next_index"],
        "expected_next": prefix_result["expected_next"],
        "selected_next": selected_next,
        "candidates": candidates,
    }


def build_payload(
    op: str,
    history: list[str],
    prefix: list[str],
    candidates: list[str],
    from_next: str | None = None,
    to_next: str | None = None,
    selected_next: str | None = None,
) -> dict[str, Any]:
    op = op.upper()

    if op == "REDIRECT":
        if from_next is None or to_next is None:
            raise ValueError("REDIRECT requires from_next and to_next")
        operation = classify_redirect(history, prefix, candidates, from_next, to_next)
    elif op == "SHADOW_SELECT":
        if selected_next is None:
            raise ValueError("SHADOW_SELECT requires selected_next")
        operation = classify_shadow_select(history, prefix, candidates, selected_next)
    else:
        raise ValueError("op must be REDIRECT or SHADOW_SELECT")

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "history": history,
        "at_history_prefix": prefix,
        "candidate_next_steps": candidates,
        "operation": operation,
    }


def print_text(payload: dict[str, Any]) -> None:
    operation = payload["operation"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"op = {operation['op']}")
    print(f"history = {payload['history']}")
    print(f"at_history_prefix = {payload['at_history_prefix']}")
    print(f"candidate_next_steps = {payload['candidate_next_steps']}")
    print(f"operation_valid = {str(operation['valid']).lower()}")
    print(f"operation_reason = {operation['reason']}")

    if operation["op"] == "REDIRECT":
        print(f"from_next = {operation['from_next']}")
        print(f"to_next = {operation['to_next']}")
    else:
        print(f"selected_next = {operation['selected_next']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG Z-axis route/history reference probe."
    )
    parser.add_argument("op", choices=["REDIRECT", "SHADOW_SELECT"])
    parser.add_argument("--history", required=True, help="JSON list of history labels")
    parser.add_argument("--prefix", required=True, help="JSON list history prefix")
    parser.add_argument(
        "--candidates",
        required=True,
        help="JSON list of candidate next-step labels",
    )
    parser.add_argument("--from-next", default=None)
    parser.add_argument("--to-next", default=None)
    parser.add_argument("--selected-next", default=None)
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    history = parse_string_list(args.history, "history")
    prefix = parse_string_list(args.prefix, "prefix")
    candidates = parse_string_list(args.candidates, "candidates")

    payload = build_payload(
        op=args.op,
        history=history,
        prefix=prefix,
        candidates=candidates,
        from_next=args.from_next,
        to_next=args.to_next,
        selected_next=args.selected_next,
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

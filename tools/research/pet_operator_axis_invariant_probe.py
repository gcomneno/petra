#!/usr/bin/env python3
"""Research-only PET/PEG operator-axis invariant probe.

This probe validates the first documented PET/PEG 2.0 operator-axis invariants
against the existing shape-level operator algebra.

It intentionally uses root arity as the shape-level proxy for baseline support
size. It does not define stable PET semantics and does not change CLI behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.pet_shape_algebra import normalize_shape, shape_apply  # noqa: E402


Shape = tuple[Any, ...]
PathT = tuple[int, ...]


SCHEMA = "pet.operator_axis_invariant_probe.v0"
CLAIM = (
    "research-only operator-axis invariant probe; root arity is used as a "
    "shape-level proxy for baseline support size"
)


OPERATOR_METADATA: dict[str, dict[str, Any]] = {
    "NEW": {
        "axis": "X",
        "class": "support-expanding",
        "expected_support_delta": 1,
        "direct_shape_mutation": True,
    },
    "DROP": {
        "axis": "X",
        "class": "support-contracting",
        "expected_support_delta": -1,
        "direct_shape_mutation": True,
    },
    "INC": {
        "axis": "Y",
        "class": "support-preserving-refinement",
        "expected_support_delta": 0,
        "direct_shape_mutation": True,
    },
    "DEC": {
        "axis": "Y",
        "class": "support-preserving-reduction",
        "expected_support_delta": 0,
        "direct_shape_mutation": True,
    },
    "REDIRECT": {
        "axis": "Z",
        "class": "connectivity-transforming",
        "expected_support_delta": 0,
        "direct_shape_mutation": False,
    },
    "SHADOW_SELECT": {
        "axis": "Z",
        "class": "shadow-connectivity",
        "expected_support_delta": 0,
        "direct_shape_mutation": False,
    },
}


DEFAULT_CASES: tuple[dict[str, Any], ...] = (
    {
        "case": "new-expands-root-support",
        "op": "NEW",
        "shape": ((),),
        "path": (),
    },
    {
        "case": "drop-contracts-root-support",
        "op": "DROP",
        "shape": ((), ((),)),
        "path": (),
    },
    {
        "case": "inc-preserves-root-support",
        "op": "INC",
        "shape": ((),),
        "path": (0,),
    },
    {
        "case": "dec-preserves-root-support",
        "op": "DEC",
        "shape": (((),),),
        "path": (0,),
    },
    {
        "case": "redirect-is-connectivity-only",
        "op": "REDIRECT",
        "shape": ((), ((),)),
        "path": (),
    },
    {
        "case": "shadow-select-is-connectivity-only",
        "op": "SHADOW_SELECT",
        "shape": ((), ((),)),
        "path": (),
    },
)


def shape_to_json(shape: Shape | None) -> list[Any] | None:
    if shape is None:
        return None
    return [shape_to_json(child) for child in shape]


def root_support_size(shape: Shape) -> int:
    return len(normalize_shape(shape))


def classify_case(case: dict[str, Any]) -> dict[str, Any]:
    op = str(case["op"]).upper()
    if op not in OPERATOR_METADATA:
        raise ValueError(f"unknown operator: {op}")

    metadata = OPERATOR_METADATA[op]
    shape = normalize_shape(case["shape"])
    path = tuple(case.get("path", ()))

    before_support = root_support_size(shape)

    row: dict[str, Any] = {
        "case": case["case"],
        "op": op,
        "axis": metadata["axis"],
        "operator_class": metadata["class"],
        "path": list(path),
        "input_shape": shape_to_json(shape),
        "root_support_before": before_support,
        "expected_support_delta": metadata["expected_support_delta"],
        "direct_shape_mutation": metadata["direct_shape_mutation"],
    }

    if metadata["axis"] == "Z":
        row.update(
            {
                "applied_shape_operator": False,
                "result_shape": shape_to_json(shape),
                "root_support_after": before_support,
                "support_delta": 0,
                "invariant_holds": not metadata["direct_shape_mutation"],
                "invariant": "Z operators are route/connectivity metadata in this probe",
            }
        )
        return row

    result_shape = normalize_shape(shape_apply(shape, op, path))
    after_support = root_support_size(result_shape)
    support_delta = after_support - before_support

    if metadata["axis"] == "X":
        invariant = "X operators change root support size"
        invariant_holds = support_delta == metadata["expected_support_delta"]
    elif metadata["axis"] == "Y":
        invariant = "Y operators preserve root support size"
        invariant_holds = support_delta == 0 and path != ()
    else:  # pragma: no cover - defensive only
        raise ValueError(f"unsupported axis for structural operator: {metadata['axis']}")

    row.update(
        {
            "applied_shape_operator": True,
            "result_shape": shape_to_json(result_shape),
            "root_support_after": after_support,
            "support_delta": support_delta,
            "invariant_holds": invariant_holds,
            "invariant": invariant,
        }
    )
    return row


def build_payload() -> dict[str, Any]:
    rows = [classify_case(case) for case in DEFAULT_CASES]
    failed = [row for row in rows if not row["invariant_holds"]]

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "rows": rows,
        "summary": {
            "checked": len(rows),
            "passed": len(rows) - len(failed),
            "failed": len(failed),
            "failed_cases": [row["case"] for row in failed],
        },
    }


def print_text(payload: dict[str, Any]) -> None:
    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print()
    for row in payload["rows"]:
        print(f"case = {row['case']}")
        print(f"op = {row['op']}")
        print(f"axis = {row['axis']}")
        print(f"operator_class = {row['operator_class']}")
        print(f"root_support_before = {row['root_support_before']}")
        print(f"root_support_after = {row['root_support_after']}")
        print(f"support_delta = {row['support_delta']}")
        print(f"direct_shape_mutation = {row['direct_shape_mutation']}")
        print(f"invariant_holds = {row['invariant_holds']}")
        print()
    summary = payload["summary"]
    print(
        "summary = "
        f"checked:{summary['checked']} "
        f"passed:{summary['passed']} "
        f"failed:{summary['failed']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG operator-axis invariant probe."
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    payload = build_payload()

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

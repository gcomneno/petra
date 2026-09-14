"""Command-line interface for verifying a proposed PETRA edit path."""

from __future__ import annotations

import argparse
import json
import sys

from petra import serialize_shape

from .verify import VerifyError, verify_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resolver-verify",
        description=(
            "Verify a proposed path between two canonical PETRA shapes."
        ),
    )
    parser.add_argument("source", help="source PETRA shape text")
    parser.add_argument("target", help="target PETRA shape text")
    parser.add_argument(
        "--steps-json",
        required=True,
        help=(
            "JSON array of steps; each step is an object with "
            "'operator' and 'target' (see PETRA invocation schema)"
        ),
    )
    parser.add_argument(
        "--no-minimal-check",
        action="store_true",
        help="skip computing the minimum distance",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=80,
    )
    parser.add_argument(
        "--max-visited",
        type=int,
        default=200_000,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a single compact JSON document",
    )
    return parser


def _result_data(result: object) -> dict[str, object]:
    # result is a VerificationResult; we keep typing loose here.
    from .verify import VerificationResult

    assert isinstance(result, VerificationResult)

    payload: dict[str, object] = {
        "schema": "resolver.verify.v1",
        "source": serialize_shape(result.source),
        "target": serialize_shape(result.target),
        "final_shape": serialize_shape(result.final_shape),
        "step_count": len(result.steps),
        "valid": result.valid,
        "minimal": result.minimal,
        "expected_length": result.expected_length,
        "reason": result.reason,
    }

    if result.failed_step is not None:
        fs = result.failed_step
        payload["failed_step"] = {
            "index": fs.index,
            "operator": fs.operator.value,
            "reason": fs.reason,
            "before_shape": serialize_shape(fs.before_shape),
        }

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        steps = json.loads(args.steps_json)
    except json.JSONDecodeError as error:
        print(
            f"resolver-verify: steps-json is not valid JSON: {error}",
            file=sys.stderr,
        )
        return 2

    if not isinstance(steps, list):
        print(
            "resolver-verify: steps-json must be a JSON array",
            file=sys.stderr,
        )
        return 2

    try:
        result = verify_path(
            args.source,
            args.target,
            steps,
            check_minimal=not args.no_minimal_check,
            max_depth=args.max_depth,
            max_nodes=args.max_nodes,
            max_visited=args.max_visited,
        )
    except (VerifyError, Exception) as error:
        print(f"resolver-verify: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                _result_data(result),
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    else:
        print(f"source = {serialize_shape(result.source)}")
        print(f"target = {serialize_shape(result.target)}")
        print(f"steps  = {len(result.steps)}")
        print(f"valid  = {result.valid}")
        if result.minimal is not None:
            print(
                f"minimal = {result.minimal} "
                f"(expected {result.expected_length})"
            )
        print(f"reason = {result.reason}")
        if result.failed_step is not None:
            fs = result.failed_step
            print()
            print(
                f"step {fs.index} failed: "
                f"{fs.operator.value} ({fs.reason})"
            )
            print(f"  before = {serialize_shape(fs.before_shape)}")

    if not result.valid:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

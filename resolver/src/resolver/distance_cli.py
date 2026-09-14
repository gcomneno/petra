"""Command-line interface for structural distance between integers."""

from __future__ import annotations

import argparse
import json
import sys

from petra import serialize_shape

from .distance import (
    DistanceError,
    int_to_shape,
    structural_distance_shapes,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resolver-distance",
        description=(
            "Compute the structural edit distance between two integers "
            "whose prime factorization is known."
        ),
    )
    parser.add_argument("a", type=int, help="first positive integer")
    parser.add_argument("b", type=int, help="second positive integer")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=30,
        help="maximum number of steps (default: 30)",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=200,
        help="maximum node count per shape (default: 200)",
    )
    parser.add_argument(
        "--max-visited",
        type=int,
        default=500_000,
        help="maximum distinct shapes explored (default: 500000)",
    )
    parser.add_argument(
        "--shapes",
        action="store_true",
        help="also print the canonical PETRA shapes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a single compact JSON document",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        shape_a = int_to_shape(args.a)
        shape_b = int_to_shape(args.b)
        distance = structural_distance_shapes(
            shape_a,
            shape_b,
            max_depth=args.max_depth,
            max_nodes=args.max_nodes,
            max_visited=args.max_visited,
        )
    except DistanceError as error:
        print(f"resolver-distance: {error}", file=sys.stderr)
        return 1

    if args.json:
        payload: dict[str, object] = {
            "schema": "resolver.distance.v1",
            "a": args.a,
            "b": args.b,
            "distance": distance,
        }
        if args.shapes:
            payload["shape_a"] = serialize_shape(shape_a)
            payload["shape_b"] = serialize_shape(shape_b)
        print(
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0

    if args.shapes:
        print(f"shape({args.a}) = {serialize_shape(shape_a)}")
        print(f"shape({args.b}) = {serialize_shape(shape_b)}")
    print(f"distance = {distance}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

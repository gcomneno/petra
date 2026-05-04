#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
from typing import Any

Shape = tuple["Shape", ...]


def _load_shape_algebra_module():
    here = Path(__file__).resolve().parent
    candidate = here / "pet_shape_algebra.py"
    if not candidate.exists():
        raise RuntimeError(f"cannot locate pet_shape_algebra.py next to {__file__}")
    spec = importlib.util.spec_from_file_location("pet_shape_algebra", candidate)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pet_shape_algebra from {candidate}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_shape_algebra_module()


def _coerce_shape(obj: Any):
    if obj is None:
        return None
    if isinstance(obj, list):
        return tuple(_coerce_shape(x) for x in obj)
    if isinstance(obj, tuple):
        return tuple(_coerce_shape(x) for x in obj)
    raise ValueError(f"unsupported shape node: {obj!r}")


def parse_shape_expr(text: str):
    obj = ast.literal_eval(text)
    return _coerce_shape(obj)


def shape_to_json(shape):
    if shape is None:
        return None
    return [shape_to_json(child) for child in shape]


def _move_to_json(move: dict) -> dict:
    return {
        "op": move["op"],
        "path": list(move["path"]),
        "result": shape_to_json(move["result"]),
    }


def _step_to_json(step: dict) -> dict:
    return {
        "op": step["op"],
        "path": list(step["path"]),
        "result": shape_to_json(step["result"]),
    }


def cmd_neighbors(args: argparse.Namespace) -> int:
    shape = mod.normalize_shape(parse_shape_expr(args.shape))
    moves = tuple(mod.shape_neighbors(shape))
    payload = {
        "shape": shape_to_json(shape),
        "neighbor_count": len(moves),
        "neighbors": tuple(_move_to_json(m) for m in moves),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"shape = {payload['shape']}")
    print(f"neighbor_count = {payload['neighbor_count']}")
    print()
    print("neighbors:")
    for i, row in enumerate(payload["neighbors"], start=1):
        print(f"  [{i}] op={row['op']} path={row['path']} result={row['result']}")
    return 0


def cmd_distance(args: argparse.Namespace) -> int:
    left = mod.normalize_shape(parse_shape_expr(args.left))
    right = mod.normalize_shape(parse_shape_expr(args.right))
    dist = mod.shape_distance(left, right, max_depth=args.max_depth)
    payload = {
        "left": shape_to_json(left),
        "right": shape_to_json(right),
        "max_depth": args.max_depth,
        "distance": dist,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"left = {payload['left']}")
    print(f"right = {payload['right']}")
    print(f"max_depth = {payload['max_depth']}")
    print(f"distance = {payload['distance']}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    start = mod.normalize_shape(parse_shape_expr(args.start))
    target = mod.normalize_shape(parse_shape_expr(args.target))
    path = tuple(mod.shape_shortest_path(start, target, max_depth=args.max_depth))
    payload = {
        "start": shape_to_json(start),
        "target": shape_to_json(target),
        "max_depth": args.max_depth,
        "distance": len(path),
        "path": tuple(_step_to_json(step) for step in path),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"start = {payload['start']}")
    print(f"target = {payload['target']}")
    print(f"max_depth = {payload['max_depth']}")
    print(f"distance = {payload['distance']}")
    print()
    print("path:")
    cur = start
    if not payload["path"]:
        print(f"  [0] already-at-target shape={shape_to_json(cur)}")
        return 0
    for i, step in enumerate(payload["path"], start=1):
        print(f"  [{i}] op={step['op']} path={step['path']} result={step['result']}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    left = mod.normalize_shape(parse_shape_expr(args.left))
    right = mod.normalize_shape(parse_shape_expr(args.right))
    path = tuple(mod.shape_shortest_path(right, left, max_depth=args.max_depth))
    payload = {
        "lhs": shape_to_json(left),
        "rhs": shape_to_json(right),
        "interpretation": "lhs ⊖ rhs := shortest rewrite path from rhs to lhs",
        "max_depth": args.max_depth,
        "cost": len(path),
        "rewrite": tuple(_step_to_json(step) for step in path),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"lhs = {payload['lhs']}")
    print(f"rhs = {payload['rhs']}")
    print(f"interpretation = {payload['interpretation']}")
    print(f"max_depth = {payload['max_depth']}")
    print(f"cost = {payload['cost']}")
    print()
    print("rewrite:")
    if not payload["rewrite"]:
        print("  [0] zero-cost (same shape)")
        return 0
    for i, step in enumerate(payload["rewrite"], start=1):
        print(f"  [{i}] op={step['op']} path={step['path']} result={step['result']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PET rewrite arithmetic v0 over exact PET shapes"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_neighbors = sub.add_parser("neighbors", help="enumerate primitive rewrite neighbors of one exact shape")
    p_neighbors.add_argument("shape")
    p_neighbors.add_argument("--json", action="store_true")
    p_neighbors.set_defaults(func=cmd_neighbors)

    p_distance = sub.add_parser("distance", help="minimum rewrite distance between two exact shapes")
    p_distance.add_argument("left")
    p_distance.add_argument("right")
    p_distance.add_argument("--max-depth", type=int, default=8)
    p_distance.add_argument("--json", action="store_true")
    p_distance.set_defaults(func=cmd_distance)

    p_path = sub.add_parser("path", help="one shortest rewrite path from start to target")
    p_path.add_argument("start")
    p_path.add_argument("target")
    p_path.add_argument("--max-depth", type=int, default=8)
    p_path.add_argument("--json", action="store_true")
    p_path.set_defaults(func=cmd_path)

    p_diff = sub.add_parser("diff", help="structural difference lhs ⊖ rhs as shortest rewrite from rhs to lhs")
    p_diff.add_argument("left")
    p_diff.add_argument("right")
    p_diff.add_argument("--max-depth", type=int, default=8)
    p_diff.add_argument("--json", action="store_true")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

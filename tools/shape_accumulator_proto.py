#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
from collections import Counter

Shape = tuple["Shape", ...]
Partial = Any


def _load_shape_algebra_module():
    path = Path(__file__).resolve().with_name("pet_shape_algebra.py")
    spec = importlib.util.spec_from_file_location("pet_shape_algebra", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pet_shape_algebra from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_shape_algebra_module()


def _coerce_partial(obj):
    if obj is None:
        return None
    if isinstance(obj, list):
        return tuple(_coerce_partial(x) for x in obj)
    if isinstance(obj, tuple):
        return tuple(_coerce_partial(x) for x in obj)
    raise ValueError(f"unsupported partial node: {obj!r}")


def parse_partial_expr(text: str):
    obj = ast.literal_eval(text)
    return _coerce_partial(obj)


def parse_path(text: str) -> tuple[int, ...]:
    if not text:
        return ()
    return tuple(int(x) for x in text.split("."))


def shape_height(shape: Shape) -> int:
    if not shape:
        return 0
    return 1 + max((shape_height(child) for child in shape), default=0)


def shape_key(shape: Shape):
    return (len(shape), tuple(shape_key(child) for child in shape))


def shape_to_json(shape):
    if shape is None:
        return None
    return [shape_to_json(child) for child in shape]


def shape_from_json(obj):
    if obj is None:
        return None
    if not isinstance(obj, list):
        raise ValueError(f"invalid shape json payload: {obj!r}")
    return tuple(shape_from_json(child) for child in obj)


def _shape_token_from_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

def _shape_token(shape: Shape) -> str:
    return _shape_token_from_json(shape_to_json(shape))

def _root_children_cover(shape: Shape, required_children_json: list) -> bool:
    have = Counter(_shape_token(child) for child in shape)
    need = Counter(_shape_token_from_json(child) for child in required_children_json)
    return all(have[k] >= v for k, v in need.items())

def _root_children_exact(shape: Shape, exact_children_json: list) -> bool:
    have = Counter(_shape_token(child) for child in shape)
    want = Counter(_shape_token_from_json(child) for child in exact_children_json)
    return have == want


def _select_candidate_row(payload: dict, rank: int) -> dict:
    if not payload["candidates"]:
        raise SystemExit("no candidates available")
    selected_row = next((row for row in payload["candidates"] if row["rank"] == rank), None)
    if selected_row is None:
        raise SystemExit(f"--candidate must be between 1 and {len(payload['candidates'])}")
    return selected_row

@lru_cache(maxsize=None)
def _load_partial_explain_oracle(target: int, schedule: int) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "partial-explain",
            str(target),
            "--schedule",
            str(schedule),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def peak_height_formula(mass: int) -> int:
    return (mass + 4) // 3


def candidate_score(shape: Shape):
    mass = mod.shape_mass(shape)
    h = shape_height(shape)
    rw = len(shape)
    return (
        abs(h - peak_height_formula(mass)),
        rw,
        -h,
        shape_key(shape),
    )



def _nth_prime(n: int) -> int:
    if n < 1:
        raise ValueError("n must be >= 1")
    primes: list[int] = []
    cand = 2
    while len(primes) < n:
        is_prime = True
        for q in primes:
            if q * q > cand:
                break
            if cand % q == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(cand)
        cand += 1 if cand == 2 else 2
    return primes[-1]


def _floor_log(base: int, limit: int) -> int:
    if limit < 1:
        return -1
    e = 0
    cur = 1
    while cur <= limit // base:
        cur *= base
        e += 1
    return e


def _exp_value_bounded(shape: Shape, limit: int) -> int | None:
    # Returns exact exponent value if <= limit, else None.
    shape = mod.normalize_shape(shape)
    if not shape:
        return 1
    total = 1
    for i, child in enumerate(shape):
        prime = _nth_prime(i + 1)
        exp_limit = _floor_log(prime, limit // total)
        if exp_limit < 0:
            return None
        child_exp = _exp_value_bounded(child, exp_limit)
        if child_exp is None:
            return None
        factor = pow(prime, child_exp)
        total *= factor
        if total > limit:
            return None
    return total


def _shape_gamma_bounded(shape: Shape, limit: int) -> int | None:
    # Returns exact gamma if <= limit, else None.
    shape = mod.normalize_shape(shape)
    total = 1
    for i, child in enumerate(shape):
        prime = _nth_prime(i + 1)
        exp_limit = _floor_log(prime, limit // total)
        if exp_limit < 0:
            return None
        exp = _exp_value_bounded(child, exp_limit)
        if exp is None:
            return None
        factor = pow(prime, exp)
        total *= factor
        if total > limit:
            return None
    return total


def _local_compat_stub(shape: Shape, *, target: int | None = None, oracle: dict | None = None) -> tuple[str, str]:
    probe = (oracle or {}).get("probe", {})
    root_lb = probe.get("root_generator_lower_bound")
    known_root_children = probe.get("known_root_children")
    exact_root_anatomy = probe.get("exact_root_anatomy")
    exact_root_children = probe.get("exact_root_children")

    if known_root_children is not None and not _root_children_cover(shape, known_root_children):
        return ("impossible", "oracle-missing-known-root-child")

    if exact_root_anatomy and exact_root_children is not None and not _root_children_exact(shape, exact_root_children):
        return ("impossible", "oracle-root-anatomy-mismatch")

    if target is None:
        if root_lb is not None:
            return ("open", f"oracle-root-lb={root_lb}")
        return ("open", "stub-no-target")

    mass = mod.shape_mass(shape)

    # Prototipo conservativo:
    # - per masse piccole usiamo gamma esatto
    # - per masse grandi usiamo per ora solo l'oracle strutturale sul root
    if mass <= 4:
        try:
            gamma = mod.shape_gamma(shape)
        except Exception:
            return ("open", "exact-gamma-failed")
        if root_lb is not None and gamma < root_lb:
            return ("impossible", "exact-gamma-below-root-generator-lb")
        if gamma == target:
            return ("certain", "exact-gamma-matches-target")
        if gamma > target:
            return ("impossible", "exact-gamma-exceeds-target")
        return ("open", "exact-gamma-below-target")

    if root_lb is not None:
        return ("open", f"oracle-root-lb={root_lb}")

    return ("open", "compat-deferred-large-mass")


def _compat_rank(status: str) -> int:
    order = {"certain": 0, "open": 1, "impossible": 2}
    return order.get(status, 9)


def _oracle_shape_rank(shape: Shape, oracle: dict | None) -> tuple[int, str]:
    if not oracle:
        return (9, "no-oracle")

    probe = oracle.get("probe", {})
    top = oracle.get("top_candidate", {})

    exact_root_children = probe.get("exact_root_children")
    top_candidate_root_children = top.get("candidate_root_children")
    known_root_children = probe.get("known_root_children")

    if exact_root_children is not None:
        if _root_children_exact(shape, exact_root_children):
            return (0, "oracle-exact-root-match")

    if top_candidate_root_children is not None:
        if _root_children_exact(shape, top_candidate_root_children):
            return (1, "oracle-top-candidate-root-match")

    if known_root_children is not None:
        if _root_children_cover(shape, known_root_children):
            return (2, "oracle-known-root-cover")

    return (9, "oracle-no-root-match")


@dataclass
class Candidate:
    rank: int
    mass: int
    height: int
    root_width: int
    peak_h: int
    score: tuple
    shape: Shape
    oracle_rank: int = 9
    compat_status: str = "open"
    compat_note: str | None = None
    gamma: int | None = None


def build_candidates(partial, max_mass: int, preview: int, with_gamma: bool, target: int | None = None, oracle: dict | None = None):
    frontier = tuple(mod.partial_shape_completion_frontier(partial, max_mass))
    enriched = []
    for shape in frontier:
        compat_status, compat_note = _local_compat_stub(shape, target=target, oracle=oracle)
        oracle_rank, oracle_note = _oracle_shape_rank(shape, oracle)
        enriched.append((shape, compat_status, compat_note, oracle_rank, oracle_note))

    ranked = sorted(
        enriched,
        key=lambda row: (_compat_rank(row[1]), row[3]) + candidate_score(row[0]),
    )

    out: list[Candidate] = []
    for i, (shape, compat_status, compat_note, oracle_rank, oracle_note) in enumerate(ranked[:preview], start=1):
        mass = mod.shape_mass(shape)
        gamma = None
        if with_gamma and mass <= 4:
            try:
                gamma = mod.shape_gamma(shape)
            except Exception:
                gamma = None
        note = compat_note
        if oracle_note and oracle_note not in {"no-oracle", "oracle-known-root-cover"}:
            note = f"{compat_note};{oracle_note}" if compat_note else oracle_note
        out.append(
            Candidate(
                rank=i,
                mass=mass,
                height=shape_height(shape),
                root_width=len(shape),
                peak_h=peak_height_formula(mass),
                score=candidate_score(shape),
                shape=shape,
                oracle_rank=oracle_rank,
                compat_status=compat_status,
                compat_note=note,
                gamma=gamma,
            )
        )
    return frontier, out


def build_state(partial, max_mass: int, preview: int, with_gamma: bool, target: int | None = None, oracle_schedule: int = 10):
    partial = mod.normalize_partial_shape(partial)
    oracle = _load_partial_explain_oracle(target, oracle_schedule) if target is not None else None
    frontier, candidates = build_candidates(partial, max_mass, preview, with_gamma, target=target, oracle=oracle)
    forced_core = mod.partial_shape_forced_core(partial, max_mass)
    free_paths = mod.partial_shape_free_paths(partial, max_mass)
    try:
        residual = mod.partial_shape_residual_summary(partial, max_mass, preview=preview, fast_preview=True)
    except TypeError:
        residual = mod.partial_shape_residual_summary(partial, max_mass, preview=preview)

    compat_summary = {"certain": 0, "open": 0, "impossible": 0}
    for c in candidates:
        compat_summary[c.compat_status] = compat_summary.get(c.compat_status, 0) + 1

    payload = {
        "partial": shape_to_json(partial),
        "is_exact": mod.partial_shape_is_exact(partial),
        "hole_count": mod.partial_shape_hole_count(partial),
        "max_mass": max_mass,
        "completion_count": len(frontier),
        "compat_summary": compat_summary,
        "oracle_schedule": oracle_schedule if target is not None else None,
        "oracle_stop_reason": (oracle or {}).get("probe", {}).get("stop_reason"),
        "oracle_known_root_generator_lower_bound": (oracle or {}).get("probe", {}).get("known_root_generator_lower_bound"),
        "oracle_root_generator_lower_bound": (oracle or {}).get("probe", {}).get("root_generator_lower_bound"),
        "oracle_known_root_children": (oracle or {}).get("probe", {}).get("known_root_children"),
        "oracle_exact_root_children": (oracle or {}).get("probe", {}).get("exact_root_children"),
        "oracle_top_candidate_root_generator": (oracle or {}).get("top_candidate", {}).get("candidate_root_generator"),
        "oracle_top_candidate_root_children": (oracle or {}).get("top_candidate", {}).get("candidate_root_children"),
        "forced_core": shape_to_json(forced_core),
        "free_paths": [list(p) for p in free_paths],
        "residual_kind": residual.get("kind"),
        "reported_in_canonical_coordinates": residual.get("reported_in_canonical_coordinates"),
        "stable_window": residual.get("stable_window"),
        "warning": residual.get("warning"),
        "candidates": [
            {
                "rank": c.rank,
                "mass": c.mass,
                "height": c.height,
                "root_width": c.root_width,
                "peak_h": c.peak_h,
                "oracle_rank": c.oracle_rank,
                "compat_status": c.compat_status,
                **({"compat_note": c.compat_note} if c.compat_note is not None else {}),
                "shape": shape_to_json(c.shape),
                **({"gamma": c.gamma} if c.gamma is not None else {}),
            }
            for c in candidates
        ],
    }
    return payload, frontier, candidates


def cmd_show(args: argparse.Namespace) -> int:
    partial = parse_partial_expr(args.partial)
    payload, _, _ = build_state(partial, args.max_mass, args.preview, args.with_gamma, target=args.target, oracle_schedule=args.oracle_schedule)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"partial = {payload['partial']}")
    print(f"is_exact = {payload['is_exact']}")
    print(f"hole_count = {payload['hole_count']}")
    print(f"max_mass = {payload['max_mass']}")
    print(f"completion_count = {payload['completion_count']}")
    print(f"compat_summary = {payload['compat_summary']}")
    if payload["oracle_stop_reason"] is not None:
        print(f"oracle_stop_reason = {payload['oracle_stop_reason']}")
    if payload["oracle_known_root_generator_lower_bound"] is not None:
        print(f"oracle_known_root_generator_lower_bound = {payload['oracle_known_root_generator_lower_bound']}")
    if payload["oracle_root_generator_lower_bound"] is not None:
        print(f"oracle_root_generator_lower_bound = {payload['oracle_root_generator_lower_bound']}")
    if payload["oracle_known_root_children"] is not None:
        print(f"oracle_known_root_children = {payload['oracle_known_root_children']}")
    if payload["oracle_exact_root_children"] is not None:
        print(f"oracle_exact_root_children = {payload['oracle_exact_root_children']}")
    if payload["oracle_top_candidate_root_generator"] is not None:
        print(f"oracle_top_candidate_root_generator = {payload['oracle_top_candidate_root_generator']}")
    if payload["oracle_top_candidate_root_children"] is not None:
        print(f"oracle_top_candidate_root_children = {payload['oracle_top_candidate_root_children']}")
    print(f"forced_core = {payload['forced_core']}")
    print(f"free_paths = {payload['free_paths']}")
    if payload["residual_kind"] is not None:
        print(f"residual_kind = {payload['residual_kind']}")
    if payload["reported_in_canonical_coordinates"] is not None:
        print(f"reported_in_canonical_coordinates = {payload['reported_in_canonical_coordinates']}")
    if payload["stable_window"] is not None:
        print(f"stable_window = {payload['stable_window']}")
    if payload["warning"] is not None:
        print(f"warning = {payload['warning']}")
    print()
    print("top_candidates:")
    for row in payload["candidates"]:
        bits = [
            f"[{row['rank']}]",
            f"compat={row['compat_status']}",
            f"oracle_rank={row['oracle_rank']}",
            f"mass={row['mass']}",
            f"height={row['height']}",
            f"root_width={row['root_width']}",
            f"peak_h={row['peak_h']}",
            f"shape={row['shape']}",
        ]
        if "compat_note" in row:
            bits.append(f"note={row['compat_note']}")
        if "gamma" in row:
            bits.append(f"gamma={row['gamma']}")
        print("  " + " ".join(bits))
    return 0


def cmd_step(args: argparse.Namespace) -> int:
    partial = parse_partial_expr(args.partial)
    payload, _, _ = build_state(
        partial,
        args.max_mass,
        args.preview,
        args.with_gamma,
        target=args.target,
        oracle_schedule=args.oracle_schedule,
    )

    selected_row = _select_candidate_row(payload, args.candidate)

    exact = shape_from_json(selected_row["shape"])
    path = parse_path(args.path)

    if args.move in {"NEW", "DROP"} and path:
        raise SystemExit(f"{args.move} only supports root path")
    if args.move in {"INC", "DEC"} and not path:
        raise SystemExit(f"{args.move} requires --path like 0 or 1.0")

    moved = mod.shape_apply(exact, args.move, path=path)
    moved_mass = mod.shape_mass(moved)

    if moved_mass > args.max_mass:
        next_state = {
            "kind": "out-of-bound",
            "moved_mass": moved_mass,
            "max_mass": args.max_mass,
        }
    else:
        moved_payload, _, _ = build_state(
            moved,
            args.max_mass,
            args.preview,
            args.with_gamma,
            target=args.target,
            oracle_schedule=args.oracle_schedule,
        )
        next_state = moved_payload

    out = {
        "selected_candidate_rank": args.candidate,
        "selected_candidate_compat": selected_row["compat_status"],
        "selected_candidate_note": selected_row.get("compat_note"),
        "selected_shape": shape_to_json(exact),
        "move": args.move,
        "path": list(path),
        "moved_shape": shape_to_json(moved),
        "next_state": next_state,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print(f"selected_candidate_rank = {args.candidate}")
    print(f"selected_candidate_compat = {selected_row['compat_status']}")
    if selected_row.get("compat_note") is not None:
        print(f"selected_candidate_note = {selected_row['compat_note']}")
    print(f"selected_shape = {out['selected_shape']}")
    print(f"move = {args.move}")
    print(f"path = {out['path']}")
    print(f"moved_shape = {out['moved_shape']}")
    print()
    print("next_state:")
    if next_state.get("kind") == "out-of-bound":
        print("  kind = out-of-bound")
        print(f"  moved_mass = {next_state['moved_mass']}")
        print(f"  max_mass = {next_state['max_mass']}")
        return 0

    print(f"  completion_count = {next_state['completion_count']}")
    print(f"  compat_summary = {next_state['compat_summary']}")
    print(f"  forced_core = {next_state['forced_core']}")
    print(f"  free_paths = {next_state['free_paths']}")
    if next_state["warning"] is not None:
        print(f"  warning = {next_state['warning']}")
    print("  top_candidates:")
    for row in next_state["candidates"]:
        bits = [
            f"[{row['rank']}]",
            f"compat={row['compat_status']}",
            f"oracle_rank={row['oracle_rank']}",
            f"mass={row['mass']}",
            f"height={row['height']}",
            f"root_width={row['root_width']}",
            f"peak_h={row['peak_h']}",
            f"shape={row['shape']}",
        ]
        if "compat_note" in row:
            bits.append(f"note={row['compat_note']}")
        if "gamma" in row:
            bits.append(f"gamma={row['gamma']}")
        print("    " + " ".join(bits))
    return 0



def _distinct_moves_for_shape(
    exact: Shape,
    *,
    max_mass: int,
    preview: int,
    with_gamma: bool,
    target: int | None,
    oracle_schedule: int,
):
    raw_moves: list[tuple[str, tuple[int, ...], Shape]] = []

    if mod.shape_can_apply(exact, "NEW", path=()):
        raw_moves.append(("NEW", (), mod.shape_apply(exact, "NEW", path=())))
    if mod.shape_can_apply(exact, "DROP", path=()):
        raw_moves.append(("DROP", (), mod.shape_apply(exact, "DROP", path=())))

    for path in mod.shape_paths(exact):
        if mod.shape_can_apply(exact, "INC", path=path):
            raw_moves.append(("INC", path, mod.shape_apply(exact, "INC", path=path)))
        if mod.shape_can_apply(exact, "DEC", path=path):
            raw_moves.append(("DEC", path, mod.shape_apply(exact, "DEC", path=path)))

    buckets: dict[tuple[str, str], dict] = {}
    for op, path, moved in raw_moves:
        key = (op, _shape_token(moved))
        row = buckets.get(key)
        if row is None:
            buckets[key] = {
                "op": op,
                "representative_path": list(path),
                "equivalent_paths": [list(path)],
                "result_shape": shape_to_json(moved),
                "moved_mass": mod.shape_mass(moved),
            }
        else:
            row["equivalent_paths"].append(list(path))

    ranked = sorted(
        buckets.values(),
        key=lambda row: (
            row["op"],
            row["moved_mass"],
            shape_key(shape_from_json(row["result_shape"])),
        ),
    )

    rows = []
    for i, row in enumerate(ranked, start=1):
        moved = shape_from_json(row["result_shape"])
        if row["moved_mass"] > max_mass:
            next_state = {
                "kind": "out-of-bound",
                "moved_mass": row["moved_mass"],
                "max_mass": max_mass,
            }
        else:
            next_payload, _, _ = build_state(
                moved,
                max_mass,
                preview,
                with_gamma,
                target=target,
                oracle_schedule=oracle_schedule,
            )
            next_state = {
                "kind": "bounded",
                "completion_count": next_payload["completion_count"],
                "compat_summary": next_payload["compat_summary"],
                "top_candidate": (next_payload["candidates"][0] if next_payload["candidates"] else None),
            }

        rows.append(
            {
                "rank": i,
                "op": row["op"],
                "representative_path": row["representative_path"],
                "equivalent_paths": row["equivalent_paths"],
                "result_shape": row["result_shape"],
                "moved_mass": row["moved_mass"],
                "next_state": next_state,
            }
        )
    return rows



def _distinct_moves_shallow_for_shape(
    exact: Shape,
    *,
    max_mass: int,
    target: int | None,
    oracle_schedule: int,
):
    oracle = _load_partial_explain_oracle(target, oracle_schedule) if target is not None else None

    raw_moves: list[tuple[str, tuple[int, ...], Shape]] = []

    if mod.shape_can_apply(exact, "NEW", path=()):
        raw_moves.append(("NEW", (), mod.shape_apply(exact, "NEW", path=())))
    if mod.shape_can_apply(exact, "DROP", path=()):
        raw_moves.append(("DROP", (), mod.shape_apply(exact, "DROP", path=())))

    for path in mod.shape_paths(exact):
        if mod.shape_can_apply(exact, "INC", path=path):
            raw_moves.append(("INC", path, mod.shape_apply(exact, "INC", path=path)))
        if mod.shape_can_apply(exact, "DEC", path=path):
            raw_moves.append(("DEC", path, mod.shape_apply(exact, "DEC", path=path)))

    buckets: dict[tuple[str, str], dict] = {}
    for op, path, moved in raw_moves:
        key = (op, _shape_token(moved))
        row = buckets.get(key)
        if row is None:
            buckets[key] = {
                "op": op,
                "representative_path": list(path),
                "equivalent_paths": [list(path)],
                "result_shape": shape_to_json(moved),
                "moved_mass": mod.shape_mass(moved),
            }
        else:
            row["equivalent_paths"].append(list(path))

    ranked = sorted(
        buckets.values(),
        key=lambda row: (
            row["op"],
            row["moved_mass"],
            shape_key(shape_from_json(row["result_shape"])),
        ),
    )

    rows = []
    for i, row in enumerate(ranked, start=1):
        moved = shape_from_json(row["result_shape"])

        if row["moved_mass"] > max_mass:
            next_state = {
                "kind": "out-of-bound",
                "compat_status": "out-of-bound",
                "compat_note": None,
                "oracle_rank": 9,
                "moved_mass": row["moved_mass"],
                "max_mass": max_mass,
            }
        else:
            compat_status, compat_note = _local_compat_stub(moved, target=target, oracle=oracle)
            oracle_rank, oracle_note = _oracle_shape_rank(moved, oracle)
            note = compat_note
            if oracle_note and oracle_note not in {"no-oracle", "oracle-known-root-cover"}:
                note = f"{note};{oracle_note}" if note else oracle_note
            next_state = {
                "kind": "shallow",
                "compat_status": compat_status,
                "compat_note": note,
                "oracle_rank": oracle_rank,
            }

        rows.append(
            {
                "rank": i,
                "op": row["op"],
                "representative_path": row["representative_path"],
                "equivalent_paths": row["equivalent_paths"],
                "result_shape": row["result_shape"],
                "moved_mass": row["moved_mass"],
                "next_state": next_state,
            }
        )
    return rows

def _greedy_move_key(row: dict):
    ns = row["next_state"]

    kind_rank = {"shallow": 0, "out-of-bound": 1}.get(ns.get("kind"), 9)
    status_rank = {
        "certain": 0,
        "open": 1,
        "impossible": 2,
        "out-of-bound": 9,
    }.get(ns.get("compat_status"), 9)

    oracle_rank = ns.get("oracle_rank", 9)
    op_rank = {"INC": 0, "NEW": 1, "DEC": 2, "DROP": 3}.get(row["op"], 9)

    rep_path = row["representative_path"]
    depth_pref = -len(rep_path) if row["op"] == "INC" else 0

    result_shape = shape_from_json(row["result_shape"])
    return (
        kind_rank,
        status_rank,
        oracle_rank,
        op_rank,
        depth_pref,
        -shape_height(result_shape),
        len(result_shape),
        row["moved_mass"],
        row["op"],
        rep_path,
    )

def cmd_greedy_walk(args: argparse.Namespace) -> int:
    partial = parse_partial_expr(args.partial)

    if mod.partial_shape_is_exact(partial):
        current_shape = mod.normalize_shape(partial)
        selected_row = {
            "rank": 1,
            "shape": shape_to_json(current_shape),
        }
    else:
        payload, _, _ = build_state(
            partial,
            args.max_mass,
            args.preview,
            args.with_gamma,
            target=args.target,
            oracle_schedule=args.oracle_schedule,
        )
        selected_row = _select_candidate_row(payload, args.candidate)
        current_shape = shape_from_json(selected_row["shape"])

    trace = []
    for step_idx in range(1, args.steps + 1):
        moves = _distinct_moves_shallow_for_shape(
            current_shape,
            max_mass=args.max_mass,
            target=args.target,
            oracle_schedule=args.oracle_schedule,
        )
        if not moves:
            trace.append(
                {
                    "step": step_idx,
                    "shape": shape_to_json(current_shape),
                    "status": "no-moves",
                }
            )
            break

        current_mass = mod.shape_mass(current_shape)

        progressive = [
            row for row in moves
            if row["next_state"]["kind"] != "out-of-bound"
            and row["next_state"].get("compat_status") in {"open", "certain"}
            and row["op"] in {"INC", "NEW"}
            and row["moved_mass"] >= current_mass
        ]

        if progressive:
            best = sorted(progressive, key=_greedy_move_key)[0]
        else:
            best = sorted(moves, key=_greedy_move_key)[0]
        trace.append(
            {
                "step": step_idx,
                "shape": shape_to_json(current_shape),
                "chosen_move": best,
            }
        )

        ns = best["next_state"]
        if ns["kind"] == "out-of-bound":
            break
        if ns["compat_status"] in {"impossible", "certain"}:
            break

        current_shape = shape_from_json(best["result_shape"])

    out = {
        "initial_candidate_rank": args.candidate,
        "initial_shape": selected_row["shape"],
        "steps_requested": args.steps,
        "trace": trace,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print(f"initial_candidate_rank = {args.candidate}")
    print(f"initial_shape = {selected_row['shape']}")
    print(f"steps_requested = {args.steps}")
    print()
    print("greedy_walk:")
    for row in trace:
        print(f"  step {row['step']}: shape={row['shape']}")
        if row.get("status") == "no-moves":
            print("      status=no-moves")
            continue

        mv = row["chosen_move"]
        print(
            f"      choose op={mv['op']} rep_path={mv['representative_path']} "
            f"eq_paths={mv['equivalent_paths']} moved_mass={mv['moved_mass']} "
            f"result_shape={mv['result_shape']}"
        )

        ns = mv["next_state"]
        if ns["kind"] == "out-of-bound":
            print(f"      next=out-of-bound moved_mass={ns['moved_mass']} max_mass={ns['max_mass']}")
        else:
            print(
                f"      next=shallow compat={ns['compat_status']} "
                f"oracle_rank={ns['oracle_rank']} "
                f"note={ns['compat_note']}"
            )
    return 0

def cmd_moves(args: argparse.Namespace) -> int:
    partial = parse_partial_expr(args.partial)

    if mod.partial_shape_is_exact(partial):
        exact = mod.normalize_shape(partial)
        selected_row = {
            "rank": 1,
            "compat_status": "exact-start",
            "compat_note": "fast-path-exact-start",
            "shape": shape_to_json(exact),
        }
    else:
        payload, _, _ = build_state(
            partial,
            args.max_mass,
            args.preview,
            args.with_gamma,
            target=args.target,
            oracle_schedule=args.oracle_schedule,
        )
        selected_row = _select_candidate_row(payload, args.candidate)
        exact = shape_from_json(selected_row["shape"])

    rows = _distinct_moves_shallow_for_shape(
        exact,
        max_mass=args.max_mass,
        target=args.target,
        oracle_schedule=args.oracle_schedule,
    )

    out = {
        "selected_candidate_rank": args.candidate,
        "selected_candidate_compat": selected_row["compat_status"],
        "selected_candidate_note": selected_row.get("compat_note"),
        "selected_shape": shape_to_json(exact),
        "distinct_move_count": len(rows),
        "moves": rows,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print(f"selected_candidate_rank = {args.candidate}")
    print(f"selected_candidate_compat = {selected_row['compat_status']}")
    if selected_row.get("compat_note") is not None:
        print(f"selected_candidate_note = {selected_row['compat_note']}")
    print(f"selected_shape = {out['selected_shape']}")
    print(f"distinct_move_count = {out['distinct_move_count']}")
    print()
    print("distinct_moves:")
    for row in rows:
        print(
            f"  [{row['rank']}] op={row['op']} rep_path={row['representative_path']} "
            f"eq_paths={row['equivalent_paths']} moved_mass={row['moved_mass']} "
            f"result_shape={row['result_shape']}"
        )
        ns = row["next_state"]
        if ns["kind"] == "out-of-bound":
            print(f"      next=out-of-bound moved_mass={ns['moved_mass']} max_mass={ns['max_mass']}")
        else:
            print(
                f"      next=shallow compat={ns['compat_status']} "
                f"oracle_rank={ns['oracle_rank']} note={ns['compat_note']}"
            )
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prototype accumulator over partial/exact PET shapes using existing partial-shape residual machinery."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_show = sub.add_parser("show", help="inspect partial shape state and ranked exact completions")
    p_show.add_argument("partial", help='partial shape expr, e.g. "(None, (None,))" or "(((),), ())"')
    p_show.add_argument("--max-mass", type=int, required=True)
    p_show.add_argument("--preview", type=int, default=10)
    p_show.add_argument("--target", type=int, help="optional target integer for oracle-backed compatibility checks")
    p_show.add_argument("--oracle-schedule", type=int, default=10)
    p_show.add_argument("--with-gamma", action="store_true", help="only computed for tiny masses in this prototype")
    p_show.add_argument("--json", action="store_true")
    p_show.set_defaults(func=cmd_show)

    p_step = sub.add_parser("step", help="pick a ranked exact candidate, apply one local move, and inspect the next state")
    p_step.add_argument("partial", help='partial shape expr, e.g. "(None, (None,))" or "(((),), ())"')
    p_step.add_argument("--max-mass", type=int, required=True)
    p_step.add_argument("--preview", type=int, default=10)
    p_step.add_argument("--candidate", type=int, default=1)
    p_step.add_argument("--target", type=int, help="optional target integer for oracle-backed compatibility checks")
    p_step.add_argument("--oracle-schedule", type=int, default=10)
    p_step.add_argument("--move", choices=["NEW", "INC", "DROP", "DEC"], required=True)
    p_step.add_argument("--path", default="", help='for INC/DEC, path like "0" or "1.0"')
    p_step.add_argument("--with-gamma", action="store_true", help="only computed for tiny masses in this prototype")
    p_step.add_argument("--json", action="store_true")
    p_step.set_defaults(func=cmd_step)

    p_moves = sub.add_parser("moves", help="enumerate distinct local moves modulo resulting shape")
    p_moves.add_argument("partial", help='partial shape expr, e.g. "(None, (None,))" or "(((),), ())"')
    p_moves.add_argument("--max-mass", type=int, required=True)
    p_moves.add_argument("--preview", type=int, default=10)
    p_moves.add_argument("--candidate", type=int, default=1)
    p_moves.add_argument("--target", type=int, help="optional target integer for oracle-backed compatibility checks")
    p_moves.add_argument("--oracle-schedule", type=int, default=10)
    p_moves.add_argument("--with-gamma", action="store_true", help="only computed for tiny masses in this prototype")
    p_moves.add_argument("--json", action="store_true")
    p_moves.set_defaults(func=cmd_moves)

    p_greedy = sub.add_parser("greedy-walk", help="follow a simple greedy policy over distinct local moves")
    p_greedy.add_argument("partial", help='partial shape expr, e.g. "(None, (None,))" or "(((),), ())"')
    p_greedy.add_argument("--max-mass", type=int, required=True)
    p_greedy.add_argument("--preview", type=int, default=10)
    p_greedy.add_argument("--candidate", type=int, default=1)
    p_greedy.add_argument("--steps", type=int, default=5)
    p_greedy.add_argument("--target", type=int, help="optional target integer for oracle-backed compatibility checks")
    p_greedy.add_argument("--oracle-schedule", type=int, default=10)
    p_greedy.add_argument("--with-gamma", action="store_true", help="only computed for tiny masses in this prototype")
    p_greedy.add_argument("--json", action="store_true")
    p_greedy.set_defaults(func=cmd_greedy_walk)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

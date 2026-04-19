from __future__ import annotations

import argparse
import ast
import json
import heapq
import pathlib
import subprocess
import sys
from collections import Counter, deque

from .atlas import atlas, draw_shape, extract_shape, print_atlas
from .algebra import distance, structural_distance
from .core import (
    decode,
    encode,
    is_prime,
    metrics_dict,
    minimal_shape_representative,
    prime_factorization,
    shape_generator,
    shape_generator_from_factorization,
    shape_signature_dict,
    validate,
)
from .io import load_json_file, render, to_json
from .metrics import extended_metrics
from .families import register_subparser as register_families_subparser, run_args as run_families
from .query import register_subparser as register_query_subparser, run_args as run_query
from .metrics import (
    is_expanding,
    is_level_uniform,
    is_linear,
    is_squarefree,
    leaf_ratio,
    profile_shape,
)




def _hide_subparser(subparsers, name: str) -> None:
    subparsers._choices_actions = [
        action for action in subparsers._choices_actions
        if getattr(action, "dest", None) != name
    ]


def _shape_to_jsonable(shape):
    if shape is None:
        return None
    return [_shape_to_jsonable(child) for child in shape]


def _jsonable_value(value):
    if isinstance(value, tuple):
        return [_jsonable_value(child) for child in value]
    if isinstance(value, list):
        return [_jsonable_value(child) for child in value]
    if isinstance(value, dict):
        return {key: _jsonable_value(val) for key, val in value.items()}
    return value


def _parse_partial_shape_arg(raw: str):
    try:
        value = ast.literal_eval(raw)
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"invalid partial shape literal: {raw}") from exc

    def _convert(obj):
        if obj is None:
            return None
        if isinstance(obj, tuple):
            return tuple(_convert(child) for child in obj)
        if isinstance(obj, list):
            return tuple(_convert(child) for child in obj)
        raise ValueError("partial shape must use only tuple/list nesting and None")

    return _convert(value)


def _format_factorization(factors):
    if not factors:
        return "1"

    parts = []
    for prime, exp in factors:
        if exp == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exp}")
    return " * ".join(parts)


def _next_new_prime(support: set[int]) -> int:
    candidate = 2
    while True:
        if candidate not in support and is_prime(candidate):
            return candidate
        candidate += 1


def _explain_moves(n: int, *, include_generators: bool = True) -> dict:
    factors = prime_factorization(n)
    support = {p for p, _ in factors}

    by_exp: dict[int, list[int]] = {}
    for prime, exp in factors:
        by_exp.setdefault(exp, []).append(prime)

    q = _next_new_prime(support)
    new_n = n * q
    target_generator_for = (lambda value: shape_signature_dict(value)['generator']) if include_generators else (lambda value: None)

    moves = {
        "new": {
            "prime": q,
            "target_n": new_n,
            "target_generator": target_generator_for(new_n),
        },
        "drop": None,
        "inc": [],
        "dec": [],
    }

    for exp in sorted(by_exp):
        primes = sorted(by_exp[exp])
        rep = primes[0]

        inc_n = n * rep
        moves["inc"].append(
            {
                "exponent": exp,
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": inc_n,
                "target_generator": target_generator_for(inc_n),
            }
        )

        if exp >= 2:
            dec_n = n // rep
            moves["dec"].append(
                {
                    "exponent": exp,
                    "count": len(primes),
                    "primes": primes,
                    "representative_prime": rep,
                    "target_n": dec_n,
                    "target_generator": target_generator_for(dec_n),
                }
            )

    if 1 in by_exp:
        primes = sorted(by_exp[1])
        rep = primes[0]
        drop_n = n // rep
        if drop_n >= 2:
            moves["drop"] = {
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": drop_n,
                "target_generator": target_generator_for(drop_n),
            }

    return moves


def _pathwise_edges_for_number(n: int) -> list[dict]:
    moves = _explain_moves(n, include_generators=False)
    edges: list[dict] = []

    new_move = moves["new"]
    edges.append(
        {
            "label": f"NEW(x{new_move['prime']})",
            "target_n": new_move["target_n"],
            "target_generator": new_move["target_generator"],
        }
    )

    drop_move = moves["drop"]
    if drop_move is not None:
        edges.append(
            {
                "label": f"DROP(p={drop_move['representative_prime']})",
                "target_n": drop_move["target_n"],
                "target_generator": drop_move["target_generator"],
            }
        )

    for row in moves["inc"]:
        edges.append(
            {
                "label": f"INC(p={row['representative_prime']},e={row['exponent']})",
                "target_n": row["target_n"],
                "target_generator": row["target_generator"],
            }
        )

    for row in moves["dec"]:
        edges.append(
            {
                "label": f"DEC(p={row['representative_prime']},e={row['exponent']})",
                "target_n": row["target_n"],
                "target_generator": row["target_generator"],
            }
        )

    return edges


def _pathwise_neighborhood(
    n: int,
    depth: int,
    max_nodes: int | None = None,
) -> dict:
    if depth <= 1:
        return {"levels": [], "truncated": False}

    frontier = {n: {"path": []}}
    levels: list[dict] = []
    seen_nodes = {n}
    truncated = False

    for level in range(1, depth + 1):
        next_targets: dict[int, dict] = {}

        for source_n, meta in sorted(frontier.items()):
            source_generator = shape_signature_dict(source_n)["generator"]

            for edge in _pathwise_edges_for_number(source_n):
                target_n = edge["target_n"]
                target_generator = edge["target_generator"]

                if target_n not in seen_nodes:
                    if max_nodes is not None and len(seen_nodes) >= max_nodes:
                        truncated = True
                        continue
                    seen_nodes.add(target_n)

                row = next_targets.setdefault(
                    target_n,
                    {
                        "n": target_n,
                        "generator": target_generator,
                        "from_numbers": set(),
                        "from_generators": set(),
                        "last_step_labels": set(),
                        "path": meta["path"] + [edge["label"]],
                    },
                )
                row["from_numbers"].add(source_n)
                row["from_generators"].add(source_generator)
                row["last_step_labels"].add(edge["label"])

        if not next_targets:
            break

        rows = []
        for target_n in sorted(next_targets):
            row = next_targets[target_n]
            rows.append(
                {
                    "n": row["n"],
                    "generator": row["generator"],
                    "from_numbers": sorted(row["from_numbers"]),
                    "from_generators": sorted(row["from_generators"]),
                    "last_step_labels": sorted(row["last_step_labels"]),
                    "path": row["path"],
                }
            )

        levels.append({"depth": level, "targets": rows})
        frontier = {row["n"]: {"path": row["path"]} for row in rows}

    return {"levels": levels, "truncated": truncated}


def _dot_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\"')


def _pathwise_dot(n: int, depth: int, max_nodes: int | None = None) -> str:
    nodes: dict[int, int] = {n: shape_signature_dict(n)["generator"]}
    edge_labels: dict[tuple[int, int], set[str]] = {}
    frontier = {n}
    seen_nodes = {n}
    truncated = False

    if depth > 1:
        for _level in range(1, depth + 1):
            next_frontier: set[int] = set()

            for source_n in sorted(frontier):
                for edge in _pathwise_edges_for_number(source_n):
                    target_n = edge["target_n"]
                    target_g = edge["target_generator"]
                    label = edge["label"]

                    if target_n not in seen_nodes:
                        if max_nodes is not None and len(seen_nodes) >= max_nodes:
                            truncated = True
                            continue
                        seen_nodes.add(target_n)
                        nodes[target_n] = target_g

                    if target_n in nodes:
                        edge_labels.setdefault((source_n, target_n), set()).add(label)
                        next_frontier.add(target_n)

            if not next_frontier:
                break

            frontier = next_frontier

    lines = [
        "digraph pet_explain {",
        "  rankdir=LR;",
        '  node [shape=box];',
    ]

    if truncated:
        lines.append('  truncated_note [shape=note,label="truncated by --max-nodes"];')

    for node_n in sorted(nodes):
        node_id = f"n_{node_n}"
        node_label = f"N={node_n}\\ng={nodes[node_n]}"
        extra = " style=bold" if node_n == n else ""
        lines.append(f'  {node_id} [label="{_dot_quote(node_label)}"{extra}];')

    for (src, dst) in sorted(edge_labels):
        labels = sorted(edge_labels[(src, dst)])
        edge_label = " / ".join(labels)
        lines.append(
            f'  n_{src} -> n_{dst} [label="{_dot_quote(edge_label)}"];'
        )

    lines.append("}")
    return "\n".join(lines)



def _greedy_dismantle(n: int) -> list[dict]:
    steps: list[dict] = []
    cur = n

    while True:
        factors = prime_factorization(cur)
        cur_g = shape_signature_dict(cur)["generator"]
        cur_fact = _format_factorization(factors)

        if len(factors) == 1 and factors[0][1] == 1:
            steps.append(
                {
                    "n": cur,
                    "factorization": cur_fact,
                    "generator": cur_g,
                    "op": "STOP",
                    "note": "prime reached",
                    "next_n": None,
                    "next_generator": None,
                }
            )
            break

        exp_gt1 = [(exp, prime) for prime, exp in factors if exp >= 2]
        if exp_gt1:
            exp, prime = sorted(exp_gt1, key=lambda item: (-item[0], item[1]))[0]
            nxt = cur // prime
            op = "DEC"
            note = f"prime={prime}, exponent={exp}->{exp - 1}"
        else:
            prime = factors[0][0]
            nxt = cur // prime
            op = "DROP"
            note = f"prime={prime}"

        nxt_g = shape_signature_dict(nxt)["generator"]
        steps.append(
            {
                "n": cur,
                "factorization": cur_fact,
                "generator": cur_g,
                "op": op,
                "note": note,
                "next_n": nxt,
                "next_generator": nxt_g,
            }
        )
        cur = nxt

    return steps


def _explain_data(
    n: int,
    pathwise_depth: int = 1,
    max_nodes: int | None = None,
) -> dict:
    tree = encode(n)
    factors = prime_factorization(n)
    signature = shape_signature_dict(n)
    metrics = metrics_dict(tree)

    return {
        "n": n,
        "pathwise_depth": pathwise_depth,
        "factorization": [{"prime": p, "exponent": e} for p, e in factors],
        "factorization_str": _format_factorization(factors),
        "generator": signature["generator"],
        "already_minimal": signature["already_minimal"],
        "child_generators": signature["child_generators"],
        "signature": signature["signature"],
        "metrics": metrics,
        "moves": _explain_moves(n),
        "max_nodes": max_nodes,
        "pathwise_neighborhood": _pathwise_neighborhood(
            n,
            pathwise_depth,
            max_nodes=max_nodes,
        ),
    }


def _dismantle_data(n: int) -> dict:
    factors = prime_factorization(n)
    signature = shape_signature_dict(n)

    return {
        "n": n,
        "factorization": [{"prime": p, "exponent": e} for p, e in factors],
        "factorization_str": _format_factorization(factors),
        "generator": signature["generator"],
        "steps": _greedy_dismantle(n),
    }





def _parse_factor_spec_file(path_str: str) -> tuple[tuple[int, int], ...]:
    payload = json.loads(pathlib.Path(path_str).read_text(encoding="utf-8"))

    trust_primes = False

    if isinstance(payload, dict):
        trust_primes = bool(payload.get("trust_primes", False))

        if "factors" not in payload:
            raise ValueError("factor spec dict must contain a 'factors' key")
        payload = payload["factors"]

    if not isinstance(payload, list):
        raise ValueError("factor spec must be a JSON list or an object with a 'factors' list")

    factors = []
    seen = set()

    for row in payload:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError("each factor row must be a pair [prime, exponent]")

        prime, exp = row
        if not isinstance(prime, int) or not isinstance(exp, int):
            raise ValueError("prime and exponent must be integers")
        if prime < 2:
            raise ValueError("prime must be >= 2")
        if exp < 1:
            raise ValueError("exponent must be >= 1")
        if not trust_primes and not is_prime(prime):
            raise ValueError(f"{prime} is not prime")
        if prime in seen:
            raise ValueError(f"duplicate prime in factor spec: {prime}")

        seen.add(prime)
        factors.append((prime, exp))

    factors.sort()

    if not factors:
        raise ValueError("factor spec cannot be empty")
    if factors[0][0] != 2:
        raise ValueError("canonical build-from-factors requires support to start at prime 2")

    support = set()
    for prime, _exp in factors:
        expected = _next_new_prime(support)
        if prime != expected:
            raise ValueError(
                f"factor support is not NEW-canonical: expected next prime {expected}, got {prime}"
            )
        support.add(prime)

    return tuple(factors)


def _factor_exp(n: int, prime: int) -> int:
    for p, exp in prime_factorization(n):
        if p == prime:
            return exp
    return 0


def _canonical_build_cost_from_factors(factors: tuple[tuple[int, int], ...]) -> int | None:
    if not factors:
        return None

    support = tuple(prime for prime, _exp in factors)
    present = set(support)
    max_prime = support[-1]

    candidate = 2
    while candidate <= max_prime:
        if is_prime(candidate) and candidate not in present:
            return None
        candidate += 1

    return (len(support) - 1) + sum(exp - 1 for _prime, exp in factors)


def _canonical_build_cost(n: int) -> int | None:
    return _canonical_build_cost_from_factors(tuple(prime_factorization(n)))


def _pet_friendliness_report(n: int) -> dict:
    if n < 2:
        raise ValueError("pet-friendliness expects an integer >= 2")

    factors = tuple(prime_factorization(n))
    factor_map = dict(factors)
    support = tuple(prime for prime, _exp in factors)
    present = set(support)
    max_prime = support[-1]

    missing = []
    candidate = 2
    while candidate <= max_prime:
        if is_prime(candidate) and candidate not in present:
            missing.append(candidate)
        candidate += 1

    canonical_build_cost = _canonical_build_cost_from_factors(factors)
    strict_pet_friendly = canonical_build_cost is not None

    relaxed_hull_support = []
    candidate = 2
    while candidate <= max_prime:
        if is_prime(candidate):
            relaxed_hull_support.append(candidate)
        candidate += 1

    relaxed_hull_factors = tuple(
        (prime, factor_map.get(prime, 1))
        for prime in relaxed_hull_support
    )

    relaxed_hull_n = 1
    for prime, exp in relaxed_hull_factors:
        relaxed_hull_n *= prime ** exp

    relaxed_hull_build_cost = (len(relaxed_hull_support) - 1) + sum(
        exp - 1 for _prime, exp in relaxed_hull_factors
    )
    relaxed_exact_extra_drop_lower_bound = len(missing)
    relaxed_exact_cost_lower_bound = (
        relaxed_hull_build_cost + relaxed_exact_extra_drop_lower_bound
    )

    return {
        "n": n,
        "factors": factors,
        "support": support,
        "support_size": len(support),
        "max_prime": max_prime,
        "strict_pet_friendly": strict_pet_friendly,
        "missing_prime_count": len(missing),
        "missing_primes_before_max": tuple(missing),
        "canonical_build_cost": canonical_build_cost,
        "relaxed_hull_n": relaxed_hull_n,
        "relaxed_hull_factors": relaxed_hull_factors,
        "relaxed_hull_support": tuple(relaxed_hull_support),
        "relaxed_hull_build_cost": relaxed_hull_build_cost,
        "relaxed_exact_extra_drop_lower_bound": relaxed_exact_extra_drop_lower_bound,
        "relaxed_exact_cost_lower_bound": relaxed_exact_cost_lower_bound,
    }


def _bytes_to_build_report(path_str: str, *, byteorder: str, signed: bool) -> dict:
    int_report = _read_int_from_bytes_file(path_str, byteorder=byteorder, signed=signed)
    build_report = _build_from_int_report(int_report["int"])

    report = dict(build_report)
    report["file"] = int_report["file"]
    report["byteorder"] = int_report["byteorder"]
    report["signed"] = int_report["signed"]
    report["byte_count"] = int_report["byte_count"]
    report["hex"] = int_report["hex"]
    report["input_n"] = int_report["int"]
    return report


def _read_int_from_bytes_file(path_str: str, *, byteorder: str, signed: bool) -> dict:
    data = pathlib.Path(path_str).read_bytes()
    value = int.from_bytes(data, byteorder=byteorder, signed=signed)
    return {
        "file": path_str,
        "byteorder": byteorder,
        "signed": signed,
        "byte_count": len(data),
        "hex": data.hex(),
        "int": value,
    }


def _build_from_int_report(n: int) -> dict:
    if n < 2:
        raise ValueError("build-from-int expects an integer >= 2")

    factors = tuple(prime_factorization(n))
    if not factors or factors[0][0] != 2:
        raise ValueError("build-from-int requires NEW-canonical support starting at prime 2")

    support = [prime for prime, _ in factors]
    expected_support = []
    candidate = 2
    while len(expected_support) < len(support):
        is_prime = True
        if candidate < 2:
            is_prime = False
        elif candidate % 2 == 0:
            is_prime = candidate == 2
        else:
            d = 3
            while d * d <= candidate:
                if candidate % d == 0:
                    is_prime = False
                    break
                d += 2
        if is_prime:
            expected_support.append(candidate)
        candidate += 1

    if support != expected_support:
        raise ValueError("build-from-int requires NEW-canonical support starting at prime 2")

    exponents = [exp for _, exp in factors]
    if any(left < right for left, right in zip(exponents, exponents[1:])):
        raise ValueError("build-from-int requires NEW-canonical support starting at prime 2")

    report = _build_from_factors_report(factors)
    report["input_n"] = n
    return report


def _build_from_factors_report(factors: tuple[tuple[int, int], ...]) -> dict:
    if not factors:
        raise ValueError("factor spec cannot be empty")
    if factors[0][0] != 2:
        raise ValueError("canonical build-from-factors requires support to start at prime 2")

    target_n = 1
    for prime, exp in factors:
        target_n *= prime ** exp

    n = 2
    path = []
    current_exp: dict[int, int] = {2: 1}

    for i, (prime, target_exp) in enumerate(factors):
        if i == 0:
            if prime != 2:
                raise RuntimeError(f"expected first prime 2, got {prime}")
        else:
            prev_n = n
            n *= prime
            current_exp[prime] = 1
            path.append(
                {
                    "source_n": prev_n,
                    "label": f"NEW(p={prime})",
                    "target_n": n,
                    "target_generator": None,
                }
            )

        while current_exp[prime] < target_exp:
            prev_n = n
            prev_exp = current_exp[prime]
            n *= prime
            current_exp[prime] = prev_exp + 1
            path.append(
                {
                    "source_n": prev_n,
                    "label": f"INC(p={prime},e={prev_exp})",
                    "target_n": n,
                    "target_generator": None,
                }
            )

    if n != target_n:
        raise RuntimeError(f"builder ended at {n}, expected {target_n}")

    return {
        "start_n": 2,
        "factors": factors,
        "target_n": target_n,
        "target_generator": shape_generator_from_factorization(list(factors)),
        "steps": len(path),
        "path": path,
    }

def _factor_exp_map(n: int) -> dict[int, int]:
    return dict(prime_factorization(n))


def _plan_target_score(n: int, target: int) -> tuple[int, int, int]:
    cur = _factor_exp_map(n)
    tgt = _factor_exp_map(target)

    primes = sorted(set(cur) | set(tgt))
    exp_l1 = sum(abs(cur.get(p, 0) - tgt.get(p, 0)) for p in primes)
    support_symdiff = len(set(cur) ^ set(tgt))
    largest_prime_gap = abs((max(cur) if cur else 1) - (max(tgt) if tgt else 1))

    return (exp_l1 + support_symdiff, support_symdiff, largest_prime_gap)


def _plan_path_best_first(start: int, target: int, max_depth: int, max_visited: int = 20000):
    if start == target:
        return []

    heap = []
    start_score = _plan_target_score(start, target)
    heapq.heappush(heap, (start_score, 0, start))

    best_depth = {start: 0}
    parent = {start: None}
    edge = {}
    visited = 0

    while heap:
        _score, depth, cur = heapq.heappop(heap)
        visited += 1
        if visited > max_visited:
            break

        if cur == target:
            path = []
            node = cur
            while parent[node] is not None:
                path.append(edge[node])
                node = parent[node]
            path.reverse()
            return path

        if depth >= max_depth:
            continue

        for row in _sorted_plan_neighbors(cur):
            nxt = row["target_n"]
            nd = depth + 1

            prev_best = best_depth.get(nxt)
            if prev_best is not None and prev_best <= nd:
                continue

            best_depth[nxt] = nd
            parent[nxt] = cur
            edge[nxt] = row
            heapq.heappush(
                heap,
                (_plan_target_score(nxt, target), nd, nxt),
            )

    return None


def _plan_move_rank(label: str) -> tuple[int, str]:
    if label.startswith("NEW("):
        return (0, label)
    if label.startswith("DROP("):
        return (1, label)
    if label.startswith("INC("):
        return (2, label)
    if label.startswith("DEC("):
        return (3, label)
    return (99, label)


def _sorted_plan_neighbors(n: int) -> list[dict]:
    return sorted(
        _plan_neighbors(n),
        key=lambda row: (_plan_move_rank(row["label"]), row["target_n"], row["label"]),
    )


def _plan_neighbors(n: int):
    moves = _explain_moves(n, include_generators=False)

    new = moves.get("new")
    if new is not None:
        yield {
            "source_n": n,
            "label": f"NEW(p={new['prime']})",
            "target_n": new["target_n"],
        }

    drop = moves.get("drop")
    if drop is not None:
        yield {
            "source_n": n,
            "label": f"DROP(p={drop['representative_prime']})",
            "target_n": drop["target_n"],
        }

    for row in moves.get("inc", []):
        yield {
            "source_n": n,
            "label": f"INC(p={row['representative_prime']},e={row['exponent']})",
            "target_n": row["target_n"],
        }

    for row in moves.get("dec", []):
        yield {
            "source_n": n,
            "label": f"DEC(p={row['representative_prime']},e={row['exponent']})",
            "target_n": row["target_n"],
        }


def _plan_path(start: int, target: int, max_depth: int):
    if start == target:
        return []

    queue = deque([start])
    seen = {start}
    depth = {start: 0}
    parent = {start: None}
    edge = {}

    while queue:
        cur = queue.popleft()
        if depth[cur] >= max_depth:
            continue

        for row in _sorted_plan_neighbors(cur):
            nxt = row["target_n"]
            if nxt in seen:
                continue

            seen.add(nxt)
            depth[nxt] = depth[cur] + 1
            parent[nxt] = cur
            edge[nxt] = row

            if nxt == target:
                path = []
                node = nxt
                while parent[node] is not None:
                    path.append(edge[node])
                    node = parent[node]
                path.reverse()
                return path

            queue.append(nxt)

    return None


def _load_shape_algebra_module():
    import importlib
    import importlib.util
    import sys
    from pathlib import Path

    try:
        return importlib.import_module("pet_shape_algebra")
    except Exception:
        pass

    path = Path(__file__).resolve().parents[2] / "tools" / "pet_shape_algebra.py"
    if not path.exists():
        raise RuntimeError(f"cannot locate pet_shape_algebra module at {path}")
    spec = importlib.util.spec_from_file_location("pet_shape_algebra", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pet_shape_algebra module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("pet_shape_algebra", module)
    spec.loader.exec_module(module)
    return module


def _shape_to_json_payload(shape):
    return [_shape_to_json_payload(child) for child in shape]


def _pet_tree_to_json_payload(tree):
    return [{"p": int(p), "e": None if exp is None else _pet_tree_to_json_payload(exp)} for p, exp in tree]


def _shape_height_local(shape) -> int:
    if not shape:
        return 0
    return 1 + max((_shape_height_local(child) for child in shape), default=0)


def _shape_key_local(shape):
    return (len(shape), tuple((_shape_key_local(child) for child in shape)))


def _run_shape_enumerate(args: argparse.Namespace) -> int:
    import json

    if args.max_mass < 1:
        raise SystemExit("--max-mass must be >= 1")
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be >= 1")

    mod = _load_shape_algebra_module()
    shapes = tuple(mod.partial_shape_completion_frontier(None, args.max_mass))
    shapes = tuple(sorted(shapes, key=lambda s: (-_shape_height_local(s), len(s), _shape_key_local(s))))
    if args.limit is not None:
        shapes = shapes[: args.limit]

    if args.json:
        rows = []
        for shape in shapes:
            row = {
                "mass": mod.shape_mass(shape),
                "height": _shape_height_local(shape),
                "root_width": len(shape),
                "shape": _shape_to_json_payload(shape),
            }
            if args.with_gamma:
                row["gamma"] = mod.shape_gamma(shape)
            if args.with_pet:
                row["pet"] = _pet_tree_to_json_payload(mod.shape_to_pet(shape))
            rows.append(row)
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    for i, shape in enumerate(shapes, start=1):
        print(f"shape {i}")
        print(f"mass: {mod.shape_mass(shape)}")
        print(f"height: {_shape_height_local(shape)}")
        print(f"root_width: {len(shape)}")
        if args.with_gamma:
            print(f"gamma: {mod.shape_gamma(shape)}")
        print(f"shape: {json.dumps(_shape_to_json_payload(shape), ensure_ascii=False)}")
        if args.with_pet:
            print(f"pet: {json.dumps(_pet_tree_to_json_payload(mod.shape_to_pet(shape)), ensure_ascii=False)}")
        if i != len(shapes):
            print()
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        prog="pet",
        description="PET — Prime Exponent Tree encoder/decoder",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # builder-from-int
    p = subparsers.add_parser(
        "builder-from-int",
        help="run the end-to-end PET builder pipeline from an integer input",
    )
    p.add_argument("n", type=int, metavar="N")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_builder_from_int_out",
        help="directory for materialized builder artifacts",
    )

    # builder-from-bytes
    p = subparsers.add_parser(
        "builder-from-bytes",
        help="decode a byte stream as an integer and run the end-to-end PET builder pipeline",
    )
    p.add_argument("file", metavar="BYTES.bin")
    p.add_argument(
        "--byteorder",
        choices=("big", "little"),
        default="big",
        help="byte order used to decode the integer (default: big)",
    )
    p.add_argument(
        "--signed",
        action="store_true",
        help="interpret the byte stream as a signed integer",
    )
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--mode",
        choices=("auto", "direct", "irsr"),
        default="auto",
        help="execution mode: direct path, hostile-aware irsr path, or auto policy (default: auto)",
    )
    p.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_builder_from_bytes_out",
        help="directory for materialized builder artifacts",
    )

    # builder-from-factors
    p = subparsers.add_parser(
        "builder-from-factors",
        help="run the end-to-end PET builder pipeline from a factor specification file",
    )
    p.add_argument("file", metavar="FACTORS.json")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_builder_from_factors_out",
        help="directory for materialized builder artifacts",
    )

    # builder-from-factorization
    p = subparsers.add_parser(
        "builder-from-factorization",
        help="run the end-to-end PET builder pipeline from a known factorization file",
    )
    p.add_argument("file", metavar="FACTORS.json")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_builder_from_factorization_out",
        help="directory for materialized builder artifacts",
    )

    p_encode = subparsers.add_parser("encode", help="encode N into PET and print JSON")
    p_encode.add_argument("n", type=int, metavar="N")
    p_encode.add_argument("--json", action="store_true")

    # decode
    p_decode = subparsers.add_parser("decode", help="decode a PET JSON file back to N")
    p_decode.add_argument("file", metavar="FILE.json")

    # render
    p_render = subparsers.add_parser("render", help="render a PET JSON file as tree")
    p_render.add_argument("file", metavar="FILE.json")

    # validate
    p_validate = subparsers.add_parser("validate", help="validate a PET JSON file")
    p_validate.add_argument("file", metavar="FILE.json")

    # generator
    p_generator = subparsers.add_parser(
        "generator",
        help="print the smallest integer having the same PET structural shape as N",
    )
    p_generator.add_argument("n", type=int, metavar="N")

    # signature
    p_signature = subparsers.add_parser(
        "signature",
        help="print the canonical structural signature of the PET shape class of N",
    )
    p_signature.add_argument("n", type=int, metavar="N")
    p_signature.add_argument("--json", action="store_true")

    # compare
    p_compare = subparsers.add_parser(
        "compare",
        help="compare two integers via PET distance and structural distance",
    )
    p_compare.add_argument("n1", type=int, metavar="N1")
    p_compare.add_argument("n2", type=int, metavar="N2")
    p_compare.add_argument("--json", action="store_true")

    # classify
    p_classify = subparsers.add_parser(
        "classify",
        help="classify one integer via PET-derived structural predicates",
    )
    p_classify.add_argument("n", type=int, metavar="N")
    p_classify.add_argument("--json", action="store_true")

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="print structural metrics for N")
    p_metrics.add_argument("n", type=int, metavar="N")
    p_metrics.add_argument("--json", action="store_true")

    # extended metrics
    p_xmetrics = subparsers.add_parser(
        "xmetrics",
        help="print extended/research metrics for N",
    )
    p_xmetrics.add_argument("n", type=int, metavar="N")
    p_xmetrics.add_argument("--json", action="store_true")

    # irsr-auto-seed-report
    p_irsr_auto_seed_report = subparsers.add_parser(
        "irsr-auto-seed-report",
        help="compare hostile semiprime auto-seed ladders and print a readable report",
    )
    p_irsr_auto_seed_report.add_argument("n", type=int, metavar="N")
    p_irsr_auto_seed_report.add_argument(
        "--preset",
        choices=("standard", "wide"),
        default="standard",
        help="predefined ladder preset to use when --sqrt-radii is not provided (default: standard)",
    )
    p_irsr_auto_seed_report.add_argument(
        "--sqrt-radii",
        action="append",
        help="comma-separated radii for one ladder; repeat to compare multiple ladders (overrides --preset)",
    )
    p_irsr_auto_seed_report.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="maximum IRSR steps per ladder run (default: 5)",
    )
    p_irsr_auto_seed_report.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_irsr_auto_seed_report_out",
        help="directory for materialized builder artifacts",
    )
    p_irsr_auto_seed_report.add_argument(
        "--output",
        help="write the rendered report or JSON payload to FILE instead of stdout",
    )
    p_irsr_auto_seed_report.add_argument("--json", action="store_true")
    p_irsr_auto_seed_report.add_argument(
        "--compact-json",
        action="store_true",
        help="with --json, omit raw per-run IRSR traces and keep only compact summaries",
    )

    # irsr-auto-seed-batch
    p_irsr_auto_seed_batch = subparsers.add_parser(
        "irsr-auto-seed-batch",
        help="write compact JSONL auto-seed comparison records for hostile semiprime inputs",
    )
    p_irsr_auto_seed_batch.add_argument("start", type=int, metavar="START")
    p_irsr_auto_seed_batch.add_argument("end", type=int, metavar="END")
    p_irsr_auto_seed_batch.add_argument(
        "--jsonl",
        required=True,
        help="write compact JSONL comparison records to FILE",
    )
    p_irsr_auto_seed_batch.add_argument(
        "--preset",
        choices=("standard", "wide"),
        default="standard",
        help="predefined ladder preset to use when --sqrt-radii is not provided (default: standard)",
    )
    p_irsr_auto_seed_batch.add_argument(
        "--sqrt-radii",
        action="append",
        help="comma-separated radii for one ladder; repeat to compare multiple ladders (overrides --preset)",
    )
    p_irsr_auto_seed_batch.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="maximum IRSR steps per ladder run (default: 5)",
    )
    p_irsr_auto_seed_batch.add_argument(
        "--artifacts-dir",
        default="/tmp/pet_irsr_auto_seed_batch_out",
        help="directory for materialized builder artifacts",
    )

    # irsr-auto-seed-batch-summary
    p_irsr_auto_seed_batch_summary = subparsers.add_parser(
        "irsr-auto-seed-batch-summary",
        help="summarize and filter compact IRSR auto-seed batch JSONL records",
    )
    p_irsr_auto_seed_batch_summary.add_argument("file", metavar="BATCH.jsonl")
    p_irsr_auto_seed_batch_summary.add_argument(
        "--status",
        action="append",
        choices=(
            "no-payload-candidates",
            "payloads-nonexact",
            "builder-attempted-no-build",
            "built",
            "built-exact-match",
        ),
        help="keep only records whose best final status matches this value; repeatable",
    )
    p_irsr_auto_seed_batch_summary.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum number of matching rows to preview (default: 20)",
    )
    p_irsr_auto_seed_batch_summary.add_argument("--json", action="store_true")

    # explain
    p_explain = subparsers.add_parser(
        "explain",
        help="explain N as PET building blocks and immediate rewrite moves",
    )
    p_explain.add_argument("n", type=int, metavar="N")
    p_explain.add_argument(
        "--pathwise-depth",
        type=int,
        default=1,
        help="pathwise neighborhood depth (default: 1)",
    )
    p_explain.add_argument(
        "--depth",
        dest="pathwise_depth",
        type=int,
        help=argparse.SUPPRESS,
    )
    p_explain.add_argument(
        "--dot",
        action="store_true",
        help="print the pathwise neighborhood as Graphviz DOT",
    )
    p_explain.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help="cap the total number of pathwise neighborhood nodes",
    )
    p_explain.add_argument("--json", action="store_true")

    # partial explain
    p_partial_explain = subparsers.add_parser(
        "partial-explain",
        help="run Partial-PET probe + hybrid synthesis and show the top candidate(s)",
    )
    p_partial_explain.add_argument("n", type=int, metavar="N")
    p_partial_explain.add_argument(
        "--schedule",
        default="100,1000,10000",
        help="comma-separated probe schedule, e.g. 10 or 100,1000,10000",
    )
    p_partial_explain.add_argument("--json", action="store_true")

    # preimage search
    p_preimage_search = subparsers.add_parser(
        "preimage-search",
        help="run profiled Partial-PET preimage search from the top ranked seed",
    )
    p_preimage_search.add_argument("n", type=int, metavar="N")
    p_preimage_search.add_argument(
        "--schedule",
        default="10",
        help="comma-separated probe schedule, e.g. 10 or 100,1000,10000",
    )
    p_preimage_search.add_argument(
        "--mode",
        choices=("quick", "deep"),
        default="quick",
        help="search profile mode (default: quick)",
    )
    p_preimage_search.add_argument(
        "--depth",
        type=int,
        default=6,
        help="search depth (default: 6)",
    )
    p_preimage_search.add_argument("--json", action="store_true")

    # dismantle
    p_dismantle = subparsers.add_parser(
        "dismantle",
        help="greedily dismantle N via PET DEC/DROP steps",
    )
    p_dismantle.add_argument("n", type=int, metavar="N")
    p_dismantle.add_argument("--json", action="store_true")

    # scan
    p_scan = subparsers.add_parser("scan", help="scan range and output JSONL dataset")
    p_scan.add_argument("start", type=int)
    p_scan.add_argument("end", type=int)
    p_scan.add_argument("--jsonl", required=True)

    # atlas
    p_atlas = subparsers.add_parser(
        "atlas",
        help="compute atlas statistics for a PET dataset",
    )
    p_atlas.add_argument("file", metavar="DATASET.jsonl")

    # shape generators
    p_generators = subparsers.add_parser(
        "shape-generators",
        help="print the first integer generating each PET structural shape",
    )
    p_generators.add_argument("file", metavar="DATASET.jsonl")
    p_generators.add_argument("--metrics", action="store_true")


    # shape-of
    p_shape_of = subparsers.add_parser(
        "shape-of",
        help="print the canonical PET shape of N",
    )
    p_shape_of.add_argument("n", type=int, metavar="N")
    p_shape_of.add_argument("--json", action="store_true")

    # shape-enumerate
    p_shape_enumerate = subparsers.add_parser(
        "shape-enumerate",
        help="enumerate exact shapes in canonical shape-first order",
    )
    p_shape_enumerate.add_argument(
        "--max-mass",
        type=int,
        required=True,
        help="maximum structural mass to enumerate",
    )
    p_shape_enumerate.add_argument(
        "--limit",
        type=int,
        help="limit number of emitted shapes after canonical sorting",
    )
    p_shape_enumerate.add_argument(
        "--json",
        action="store_true",
        help="emit JSON array instead of text output",
    )
    p_shape_enumerate.add_argument(
        "--with-pet",
        action="store_true",
        help="include the minimal PET witness for each shape",
    )
    p_shape_enumerate.add_argument(
        "--with-gamma",
        action="store_true",
        help="include gamma (can grow extremely fast for height-first shapes)",
    )

    # partial-shape-report
    p_partial_shape_report = subparsers.add_parser(
        "partial-shape-report",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_report.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_report.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_report.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many exact completions to preview (default: 5)",
    )
    p_partial_shape_report.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-report")


    # partial-shape-match
    p_partial_shape_match = subparsers.add_parser(
        "partial-shape-match",
        help="check whether N matches a given partial PET shape",
    )
    p_partial_shape_match.add_argument("n", type=int, metavar="N")
    p_partial_shape_match.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_match.add_argument("--json", action="store_true")


    # partial-shape-witness
    p_partial_shape_witness = subparsers.add_parser(
        "partial-shape-witness",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_witness.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_witness.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-witness")


    # partial-shape-completions
    p_partial_shape_completions = subparsers.add_parser(
        "partial-shape-completions",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_completions.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_completions.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_completions.add_argument(
        "--preview",
        type=int,
        default=20,
        help="how many completions to print (default: 20)",
    )
    p_partial_shape_completions.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-completions")


    # partial-shape-forced-core
    p_partial_shape_forced_core = subparsers.add_parser(
        "partial-shape-forced-core",
        help="compute the bounded forced core shared by exact completions of a partial PET shape",
    )
    p_partial_shape_forced_core.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_forced_core.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_forced_core.add_argument(
        "--trace",
        action="store_true",
        help="show the cumulative forced-core trace for each bound up to --max-mass",
    )
    p_partial_shape_forced_core.add_argument(
        "--window",
        type=int,
        default=1,
        help="require an observed stabilization window of at least this many masses (default: 1)",
    )
    p_partial_shape_forced_core.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_forced_core.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_forced_core.add_argument("--json", action="store_true")


    # partial-shape-residual
    p_partial_shape_residual = subparsers.add_parser(
        "partial-shape-residual",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_residual.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded forced-core analysis (default: 3)",
    )
    p_partial_shape_residual.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-residual")


    # partial-shape-residual-profile
    p_partial_shape_residual_profile = subparsers.add_parser(
        "partial-shape-residual-profile",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_residual_profile.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual_profile.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded residual profiling (default: 3)",
    )
    p_partial_shape_residual_profile.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_residual_profile.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual_profile.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual_profile.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-residual-profile")


    # partial-shape-residual-summary
    p_partial_shape_residual_summary = subparsers.add_parser(
        "partial-shape-residual-summary",
        help="print a compact canonical summary of forced core vs residual freedom",
    )
    p_partial_shape_residual_summary.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual_summary.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded residual summary (default: 3)",
    )
    p_partial_shape_residual_summary.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_residual_summary.add_argument(
        "--fast-preview",
        action="store_true",
        help="skip expensive exact local-forced-core computation and only show preview shapes/gammas",
    )
    p_partial_shape_residual_summary.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual_summary.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual_summary.add_argument("--json", action="store_true")


    # partial-shape-target
    p_partial_shape_target = subparsers.add_parser(
        "partial-shape-target",
        help="print the observed compatible decomposition: core + residual freedom",
    )
    p_partial_shape_target.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_target.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded observed decomposition (default: 3)",
    )
    p_partial_shape_target.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_target.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_target.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_target.add_argument(
        "--fast-preview",
        action="store_true",
        help="skip expensive exact local-forced-core computation and only show preview shapes/gammas",
    )
    p_partial_shape_target.add_argument("--json", action="store_true")


    # plan
    p_plan = subparsers.add_parser(
        "plan",
        aliases=["branch-plan"],
        help="find a bounded PET move path from A to B",
    )
    p_plan.add_argument("start", type=int, metavar="A")
    p_plan.add_argument("target", type=int, metavar="B")
    p_plan.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="maximum BFS depth for bounded PET planning (default: 8)",
    )
    p_plan.add_argument("--json", action="store_true")





    # pet-friendliness
    p_pet_friendliness = subparsers.add_parser(
        "pet-friendliness",
        help="inspect whether N is PET-friendly under strict NEW-canonical support",
    )
    p_pet_friendliness.add_argument("n", type=int, metavar="N")
    p_pet_friendliness.add_argument("--json", action="store_true")

    # bytes-to-build
    p_bytes_to_build = subparsers.add_parser(
        "bytes-to-build",
        help="decode a byte stream as an integer and build it when support is NEW-canonical",
    )
    p_bytes_to_build.add_argument("file", metavar="BYTES.bin")
    p_bytes_to_build.add_argument(
        "--byteorder",
        choices=("big", "little"),
        default="big",
        help="byte order used to decode the integer (default: big)",
    )
    p_bytes_to_build.add_argument(
        "--signed",
        action="store_true",
        help="interpret the byte stream as a signed integer",
    )
    p_bytes_to_build.add_argument("--json", action="store_true")

    # int-from-bytes
    p_int_from_bytes = subparsers.add_parser(
        "int-from-bytes",
        help="read a byte stream file and interpret it as an integer",
    )
    p_int_from_bytes.add_argument("file", metavar="BYTES.bin")
    p_int_from_bytes.add_argument(
        "--byteorder",
        choices=("big", "little"),
        default="big",
        help="byte order used to decode the integer (default: big)",
    )
    p_int_from_bytes.add_argument(
        "--signed",
        action="store_true",
        help="interpret the byte stream as a signed integer",
    )
    p_int_from_bytes.add_argument("--json", action="store_true")


    # build-from-int
    p_build_from_int = subparsers.add_parser(
        "build-from-int",
        help="factor an integer and build it from ground generator 2 when support is NEW-canonical",
    )
    p_build_from_int.add_argument("n", type=int, metavar="N")
    p_build_from_int.add_argument("--json", action="store_true")
    p_build_from_int.add_argument(
        "--allow-non-canonical-support",
        action="store_true",
        help="build canonical shape first, then report pending non-canonical support realization",
    )

    # build-from-factors
    p_build_from_factors = subparsers.add_parser(
        "build-from-factors",
        help="build a NEW-canonical factorization from ground generator 2",
    )
    p_build_from_factors.add_argument("file", metavar="FACTORS.json")
    p_build_from_factors.add_argument("--json", action="store_true")


    # plan-best
    p_plan_best = subparsers.add_parser(
        "plan-best",
        aliases=["branch-plan-best"],
        help="find a bounded deterministic PET path from A to B with best-first search",
    )
    p_plan_best.add_argument("start", type=int, metavar="A")
    p_plan_best.add_argument("target", type=int, metavar="B")
    p_plan_best.add_argument(
        "--max-depth",
        type=int,
        default=12,
        help="maximum search depth for bounded best-first PET planning (default: 12)",
    )
    p_plan_best.add_argument(
        "--max-visited",
        type=int,
        default=20000,
        help="maximum popped states before giving up (default: 20000)",
    )
    p_plan_best.add_argument("--json", action="store_true")

    # branch-neighbors
    p_branch_neighbors = subparsers.add_parser(
        "branch-neighbors",
        help="show canonical deterministic PET branch moves from N",
    )
    p_branch_neighbors.add_argument("n", type=int, metavar="N")
    p_branch_neighbors.add_argument("--json", action="store_true")

    # rewrite
    p_rewrite = subparsers.add_parser(
        "rewrite",
        help="PET-METICA rewrite distance, scans, and pairwise matrices",
    )
    rewrite_subparsers = p_rewrite.add_subparsers(
        dest="rewrite_command",
        metavar="REWRITE_COMMAND",
    )
    rewrite_subparsers.required = True

    p_rewrite_pair = rewrite_subparsers.add_parser(
        "pair",
        help="compute canonical rewrite difference between two numbers",
    )
    p_rewrite_pair.add_argument("src", type=int, metavar="SRC")
    p_rewrite_pair.add_argument("dst", type=int, metavar="DST")
    p_rewrite_pair.add_argument("--overscan", type=int, default=90)
    p_rewrite_pair.add_argument("--json", action="store_true")

    p_rewrite_scan = rewrite_subparsers.add_parser(
        "scan",
        help="global PET-METICA scan over 1..N with overscan",
    )
    p_rewrite_scan.add_argument("--n-max", type=int, default=30)
    p_rewrite_scan.add_argument("--overscan", type=int, default=90)
    p_rewrite_scan.add_argument("--limit", type=int, default=10)
    p_rewrite_scan.add_argument("--json", action="store_true")

    p_rewrite_matrix = rewrite_subparsers.add_parser(
        "matrix",
        help="emit all pair rewrite distances as JSON",
    )
    p_rewrite_matrix.add_argument("--n-max", type=int, default=30)
    p_rewrite_matrix.add_argument("--overscan", type=int, default=90)
    p_rewrite_matrix.add_argument("--json", action="store_true")

    # query / families
    register_query_subparser(subparsers)
    register_families_subparser(subparsers)

    args = parser.parse_args(argv[1:])

    try:
        if args.command == "encode":
            tree = encode(args.n)
            if args.json:
                print(to_json(tree))
            else:
                back = decode(tree)
                print(f"N = {args.n}")
                print(to_json(tree))
                print(f"decoded = {back}")

        elif args.command == "shape-enumerate":
            return _run_shape_enumerate(args)

        elif args.command == "decode":
            tree = load_json_file(args.file)
            print(decode(tree))

        elif args.command == "render":
            tree = load_json_file(args.file)
            print(render(tree))

        elif args.command == "validate":
            tree = load_json_file(args.file)
            validate(tree)
            print("OK")

        elif args.command == "generator":
            print(shape_generator(args.n))

        elif args.command == "signature":
            data = shape_signature_dict(args.n)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(f"signature = {data['signature']}")

                def _list_to_tuple_shape(obj):
                    if isinstance(obj, list):
                        return tuple(_list_to_tuple_shape(child) for child in obj)
                    return obj

                print("shape:")
                shape = _list_to_tuple_shape(data["signature"])
                lines = draw_shape(shape, lines=[])
                for line in lines:
                    print(line)

        elif args.command == "compare":
            tree1 = encode(args.n1)
            tree2 = encode(args.n2)
            data = {
                "n1": args.n1,
                "n2": args.n2,
                "distance": distance(tree1, tree2),
                "structural_distance": structural_distance(tree1, tree2),
                "same_shape": structural_distance(tree1, tree2) == 0,
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N1 = {args.n1}")
                print(f"N2 = {args.n2}")
                for key, value in data.items():
                    if key in {"n1", "n2"}:
                        continue
                    print(f"{key} = {value}")

        elif args.command == "classify":
            tree = encode(args.n)
            data = {
                "n": args.n,
                "is_linear": is_linear(tree),
                "is_level_uniform": is_level_uniform(tree),
                "is_expanding": is_expanding(tree),
                "is_squarefree": is_squarefree(tree),
                "leaf_ratio": str(leaf_ratio(tree)),
                "profile_shape": profile_shape(tree),
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    if key == "n":
                        continue
                    print(f"{key} = {value}")

        elif args.command == "metrics":
            tree = encode(args.n)
            if args.json:
                print(json.dumps(metrics_dict(tree), indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in metrics_dict(tree).items():
                    print(f"{key} = {value}")

        elif args.command == "xmetrics":
            tree = encode(args.n)
            data = extended_metrics(tree)
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    print(f"{key} = {value}")

        elif args.command == "irsr-auto-seed-report":
            from pet.irsr_state import (
                compare_hostile_semiprime_auto_seed_runs,
                format_hostile_semiprime_auto_seed_comparison_report,
                summarize_hostile_semiprime_auto_seed_comparison,
            )

            if args.n < 2:
                raise ValueError("irsr-auto-seed-report expects N >= 2")
            if args.max_steps < 1:
                raise ValueError("--max-steps must be >= 1")
            if args.compact_json and not args.json:
                raise ValueError("--compact-json requires --json")

            preset_specs = {
                "standard": ["1", "4"],
                "wide": ["1", "2,4"],
            }

            raw_specs = args.sqrt_radii or preset_specs[args.preset]

            auto_seed_specs = []
            for raw in raw_specs:
                parts = [part.strip() for part in raw.split(",")]
                if not parts or any(not part for part in parts):
                    raise ValueError("--sqrt-radii must be a comma-separated list of integers")

                radii = []
                for part in parts:
                    try:
                        radius = int(part)
                    except ValueError as exc:
                        raise ValueError("--sqrt-radii must contain only integers") from exc
                    if radius < 0:
                        raise ValueError("--sqrt-radii values must be >= 0")
                    radii.append(radius)

                auto_seed_specs.append(
                    {
                        "name": "sqrt-auto-" + "-".join(f"r{radius}" for radius in radii),
                        "sqrt_radii": radii,
                    }
                )

            result = compare_hostile_semiprime_auto_seed_runs(
                args.n,
                auto_seed_specs=auto_seed_specs,
                max_steps=args.max_steps,
                output_dir=pathlib.Path(args.artifacts_dir),
            )
            summary = summarize_hostile_semiprime_auto_seed_comparison(result)
            report = format_hostile_semiprime_auto_seed_comparison_report(result)

            selection = {
                "mode": "manual" if args.sqrt_radii else "preset",
                "preset": None if args.sqrt_radii else args.preset,
                "sqrt_radii_specs": [list(spec["sqrt_radii"]) for spec in auto_seed_specs],
            }

            if args.json:
                payload_result = result
                json_mode = "full"

                if args.compact_json:
                    json_mode = "compact"
                    compact_runs = [
                        {key: value for key, value in run.items() if key != "run"}
                        for run in result["runs"]
                    ]
                    compact_best_run = result["best_run"]
                    if compact_best_run is not None:
                        compact_best_run = {
                            key: value for key, value in compact_best_run.items()
                            if key != "run"
                        }
                    payload_result = {
                        "input": result["input"],
                        "runs": compact_runs,
                        "best_run": compact_best_run,
                    }

                payload = dict(payload_result)
                payload["json_mode"] = json_mode
                payload["selection"] = selection
                payload["summary"] = summary
                payload["report"] = report
                rendered = json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False) + "\n"
            else:
                rendered = (
                    "Selection: "
                    + (
                        f"preset={selection['preset']}"
                        if selection["mode"] == "preset"
                        else "manual"
                    )
                    + "\n"
                    + f"Radii specs: {selection['sqrt_radii_specs']}\n"
                    + report
                    + "\n"
                )

            if args.output:
                pathlib.Path(args.output).write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")

        elif args.command == "irsr-auto-seed-batch":
            from pet.irsr_state import (
                compare_hostile_semiprime_auto_seed_runs,
                format_hostile_semiprime_auto_seed_comparison_report,
                summarize_hostile_semiprime_auto_seed_comparison,
            )
            from .scan import write_jsonl

            if args.start < 2:
                raise ValueError("irsr-auto-seed-batch expects START >= 2")
            if args.end < args.start:
                raise ValueError("--end must be >= --start")
            if args.max_steps < 1:
                raise ValueError("--max-steps must be >= 1")

            preset_specs = {
                "standard": ["1", "4"],
                "wide": ["1", "2,4"],
            }

            raw_specs = args.sqrt_radii or preset_specs[args.preset]

            auto_seed_specs = []
            for raw in raw_specs:
                parts = [part.strip() for part in raw.split(",")]
                if not parts or any(not part for part in parts):
                    raise ValueError("--sqrt-radii must be a comma-separated list of integers")

                radii = []
                for part in parts:
                    try:
                        radius = int(part)
                    except ValueError as exc:
                        raise ValueError("--sqrt-radii must contain only integers") from exc
                    if radius < 0:
                        raise ValueError("--sqrt-radii values must be >= 0")
                    radii.append(radius)

                auto_seed_specs.append(
                    {
                        "name": "sqrt-auto-" + "-".join(f"r{radius}" for radius in radii),
                        "sqrt_radii": radii,
                    }
                )

            selection = {
                "mode": "manual" if args.sqrt_radii else "preset",
                "preset": None if args.sqrt_radii else args.preset,
                "sqrt_radii_specs": [list(spec["sqrt_radii"]) for spec in auto_seed_specs],
            }

            output_root = pathlib.Path(args.artifacts_dir)
            output_root.mkdir(parents=True, exist_ok=True)

            records = []
            for n in range(args.start, args.end + 1):
                result = compare_hostile_semiprime_auto_seed_runs(
                    n,
                    auto_seed_specs=auto_seed_specs,
                    max_steps=args.max_steps,
                    output_dir=output_root / f"n_{n}",
                )
                summary = summarize_hostile_semiprime_auto_seed_comparison(result)
                report = format_hostile_semiprime_auto_seed_comparison_report(result)

                compact_runs = [
                    {key: value for key, value in run.items() if key != "run"}
                    for run in result["runs"]
                ]
                compact_best_run = result["best_run"]
                if compact_best_run is not None:
                    compact_best_run = {
                        key: value for key, value in compact_best_run.items()
                        if key != "run"
                    }

                records.append(
                    {
                        "schema": "irsr-auto-seed-report-batch-v1",
                        "json_mode": "compact",
                        "input": result["input"],
                        "selection": selection,
                        "summary": summary,
                        "best_run": compact_best_run,
                        "runs": compact_runs,
                        "report": report,
                    }
                )

            write_jsonl(records, args.jsonl)

        elif args.command == "irsr-auto-seed-batch-summary":
            if args.limit < 1:
                raise ValueError("--limit must be >= 1")

            path = pathlib.Path(args.file)
            if not path.exists():
                raise ValueError(f"file not found: {args.file}")

            best_status_counts = Counter()
            best_run_counts = Counter()
            matches = []

            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    row = json.loads(line)
                    summary = row["summary"]
                    best_status = summary["best_final_status"]
                    best_run_name = summary["best_run_name"]
                    n = row["input"]["n"]
                    selection = row.get("selection", {})

                    best_status_counts[best_status] += 1
                    if best_run_name is not None:
                        best_run_counts[best_run_name] += 1

                    if args.status and best_status not in args.status:
                        continue

                    matches.append(
                        {
                            "n": n,
                            "best_run_name": best_run_name,
                            "best_final_status": best_status,
                            "selection_mode": selection.get("mode"),
                            "selection_preset": selection.get("preset"),
                            "sqrt_radii_specs": selection.get("sqrt_radii_specs"),
                        }
                    )

            payload = {
                "schema": "irsr-auto-seed-batch-summary-v1",
                "file": str(path),
                "selected_statuses": [] if args.status is None else list(args.status),
                "total_records": sum(best_status_counts.values()),
                "best_status_counts": dict(sorted(best_status_counts.items())),
                "best_run_counts": dict(sorted(best_run_counts.items())),
                "matching_count": len(matches),
                "matches": matches[: args.limit],
            }

            if args.json:
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"File: {payload['file']}")
                print(f"Total records: {payload['total_records']}")
                if payload["selected_statuses"]:
                    print(f"Selected statuses: {payload['selected_statuses']}")
                best_status_counts_text = ", ".join(
                    f"{status}={count}"
                    for status, count in payload["best_status_counts"].items()
                )
                print(f"Best status counts: {best_status_counts_text}")
                best_run_counts_text = ", ".join(
                    f"{name}={count}"
                    for name, count in payload["best_run_counts"].items()
                )
                print(f"Best run counts: {best_run_counts_text}")
                print(f"Matching records: {payload['matching_count']}")
                print(f"Matches (limit={args.limit}):")
                for row in payload["matches"]:
                    print(
                        f"- n={row['n']} | "
                        f"best_run={row['best_run_name']} | "
                        f"best_status={row['best_final_status']} | "
                        f"mode={row['selection_mode']} | "
                        f"preset={row['selection_preset']} | "
                        f"radii={row['sqrt_radii_specs']}"
                    )

        elif args.command == "explain":
            if args.pathwise_depth < 1:
                raise ValueError("--pathwise-depth must be >= 1")
            if args.max_nodes is not None and args.max_nodes < 1:
                raise ValueError("--max-nodes must be >= 1")
            if args.json and args.dot:
                raise ValueError("--json and --dot cannot be used together")

            data = _explain_data(
                args.n,
                pathwise_depth=args.pathwise_depth,
                max_nodes=args.max_nodes,
            )

            if args.dot:
                print(_pathwise_dot(args.n, args.pathwise_depth, max_nodes=args.max_nodes))
            elif args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"factorization = {data['factorization_str']}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(
                    "metrics =",
                    f"nodes={data['metrics']['node_count']}",
                    f"height={data['metrics']['height']}",
                    f"max_branching={data['metrics']['max_branching']}",
                    f"recursive_mass={data['metrics']['recursive_mass']}",
                )

                print("moves:")
                new_move = data["moves"]["new"]
                print(
                    "  NEW:",
                    f"x{new_move['prime']}",
                    f"-> N'={new_move['target_n']}",
                    f"generator={new_move['target_generator']}",
                )

                drop_move = data["moves"]["drop"]
                if drop_move is None:
                    print("  DROP: unavailable")
                else:
                    print(
                        "  DROP:",
                        f"primes={drop_move['primes']}",
                        f"representative={drop_move['representative_prime']}",
                        f"-> N'={drop_move['target_n']}",
                        f"generator={drop_move['target_generator']}",
                    )

                if data["moves"]["inc"]:
                    print("  INC:")
                    for row in data["moves"]["inc"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )

                if data["moves"]["dec"]:
                    print("  DEC:")
                    for row in data["moves"]["dec"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )
                else:
                    print("  DEC: unavailable")

                neighborhood = data["pathwise_neighborhood"]
                if neighborhood["levels"]:
                    cap = ""
                    if data["max_nodes"] is not None:
                        cap = f", max_nodes={data['max_nodes']}"
                    print(f"pathwise neighborhood (depth={data['pathwise_depth']}{cap}):")
                    for level in neighborhood["levels"]:
                        print(f"  depth {level['depth']}:")
                        for row in level["targets"]:
                            print(
                                "   ",
                                f"n={row['n']}",
                                f"g={row['generator']}",
                                f"from_n={row['from_numbers']}",
                                f"from_g={row['from_generators']}",
                                f"via={row['last_step_labels']}",
                                f"path={' -> '.join(row['path'])}",
                            )
                    if neighborhood["truncated"]:
                        print("  [truncated by --max-nodes]")

        elif args.command == "partial-explain":
            if args.n < 1:
                raise ValueError("N must be >= 1")

            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            import tools.partial_signature_probe as probe_mod
            from tools.partial_explain import build_partial_explain, render_human

            schedule = probe_mod.parse_schedule(args.schedule)
            data = build_partial_explain(args.n, schedule)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(render_human(data))

        elif args.command == "preimage-search":
            if args.n < 1:
                raise ValueError("N must be >= 1")
            if args.depth < 1:
                raise ValueError("--depth must be >= 1")

            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            import tools.partial_signature_probe as probe_mod
            from tools.partial_explain import build_partial_explain
            from tools.pet_preimage_seed import (
                build_seed,
                build_profiled_search_report,
            )

            schedule = probe_mod.parse_schedule(args.schedule)
            partial = build_partial_explain(args.n, schedule)
            seed = build_seed(partial, rank=1)
            report = build_profiled_search_report(seed, depth=args.depth, mode=args.mode)

            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"N = {report['source_n']}")
                print(f"mode = {report['mode']}")
                print(f"depth = {report['depth']}")
                print(f"profile = {report['profile']}")
                print(f"frontier_count = {report['frontier_count']}")
                print(f"min_n = {report['min_n']}")
                print(f"max_n = {report['max_n']}")
                print(f"sample_ns = {report['sample_ns']}")

        elif args.command == "dismantle":
            data = _dismantle_data(args.n)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"factorization = {data['factorization_str']}")
                print(f"generator = {data['generator']}")
                print("greedy dismantle:")
                for step in data["steps"]:
                    if step["op"] == "STOP":
                        print(
                            "   ",
                            f"STOP at N={step['n']}",
                            f"({step['factorization']})",
                            f"generator={step['generator']}",
                        )
                    else:
                        print(
                            "   ",
                            f"N={step['n']}",
                            f"({step['factorization']})",
                            f"[g={step['generator']}]",
                            f"--{step['op']} {step['note']}-->",
                            f"{step['next_n']}",
                            f"[g={step['next_generator']}]",
                        )

        elif args.command == "scan":
            from .scan import scan_range, write_jsonl

            if args.start < 2:
                raise ValueError("start must be >= 2")

            if args.end < args.start:
                raise ValueError("end must be >= start")

            records = scan_range(args.start, args.end)
            write_jsonl(records, args.jsonl)

        elif args.command == "atlas":
            stats = atlas(args.file)
            print_atlas(stats)

        elif args.command == "shape-generators":
            seen = set()
            index = 0
            generators = []

            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)

                    n = rec["n"]
                    tree = rec["pet"]
                    metrics = rec["metrics"]

                    shape = extract_shape(tree)

                    if shape not in seen:
                        seen.add(shape)
                        index += 1
                        generators.append(n)

                        print()
                        print(f"shape {index}")
                        print(f"generator: {n}")

                        if args.metrics:
                            print(
                                "metrics:",
                                f"nodes={metrics['node_count']}",
                                f"height={metrics['height']}",
                                f"max_branching={metrics['max_branching']}",
                                f"recursive_mass={metrics['recursive_mass']}",
                            )

                        lines = draw_shape(shape, lines=[])

                        for line in lines:
                            print(line)

            print()
            print("generator sequence G(k):")
            print(generators)








        elif args.command == "pet-friendliness":
            report = _pet_friendliness_report(args.n)

            if args.json:
                print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
            else:
                print(f"N = {report['n']}")
                print(f"factors = {_format_factorization(report['factors'])}")
                print(f"support = {report['support']}")
                print(f"support_size = {report['support_size']}")
                print(f"max_prime = {report['max_prime']}")
                print(f"strict_pet_friendly = {'yes' if report['strict_pet_friendly'] else 'no'}")
                print(f"missing_prime_count = {report['missing_prime_count']}")
                print(f"missing_primes_before_max = {report['missing_primes_before_max']}")
                print(
                    "canonical_build_cost = "
                    + ("none" if report["canonical_build_cost"] is None else str(report["canonical_build_cost"]))
                )
                print(f"relaxed_hull_support = {report['relaxed_hull_support']}")
                print(f"relaxed_hull_factors = {_format_factorization(report['relaxed_hull_factors'])}")
                print(f"relaxed_hull_n = {report['relaxed_hull_n']}")
                print(f"relaxed_hull_build_cost = {report['relaxed_hull_build_cost']}")
                print(
                    "relaxed_exact_extra_drop_lower_bound = "
                    f"{report['relaxed_exact_extra_drop_lower_bound']}"
                )
                print(
                    "relaxed_exact_cost_lower_bound = "
                    f"{report['relaxed_exact_cost_lower_bound']}"
                )

        elif args.command == "bytes-to-build":
            report = _bytes_to_build_report(
                args.file,
                byteorder=args.byteorder,
                signed=args.signed,
            )

            if args.json:
                print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
            else:
                print(f"file = {report['file']}")
                print(f"byteorder = {report['byteorder']}")
                print(f"signed = {'yes' if report['signed'] else 'no'}")
                print(f"byte_count = {report['byte_count']}")
                print(f"hex = {report['hex']}")
                print(f"input_n = {report['input_n']}")
                print(f"factors = {_format_factorization(report['factors'])}")
                print(f"target_n = {report['target_n']}")
                print(f"target_generator = {report['target_generator']}")
                print(f"steps = {report['steps']}")
                for row in report["path"]:
                    print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command == "builder-from-int":
            from pet.builder_from_int import build_from_int_pipeline

            payload = build_from_int_pipeline(args.n, args.artifacts_dir)

            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
            else:
                final_output = payload.get("final_build_output", {})
                built = final_output.get("built_pet_object", {})
                print(f"input_n = {payload.get('input_n')}")
                print(f"schema = {payload.get('schema')}")
                print(f"build_status = {final_output.get('build_status')}")
                print(f"assembly_status = {built.get('assembly_status')}")
                print(f"component_count = {built.get('component_count')}")
                print(f"artifacts_dir = {args.artifacts_dir}")

        elif args.command == "builder-from-bytes":
            from pet.builder_from_bytes import build_from_bytes_pipeline

            payload = build_from_bytes_pipeline(
                args.file,
                args.artifacts_dir,
                byteorder=args.byteorder,
                signed=args.signed,
                mode=args.mode,
            )

            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
            else:
                builder_report = payload.get("builder_report") or {}
                final_output = builder_report.get("final_build_output", {})
                built = final_output.get("built_pet_object", {})
                terminal_state = payload.get("terminal_state") or {}

                print(f"file = {payload.get('file')}")
                print(f"byteorder = {payload.get('byteorder')}")
                print(f"signed = {'yes' if payload.get('signed') else 'no'}")
                print(f"byte_count = {payload.get('byte_count')}")
                print(f"hex = {payload.get('hex')}")
                print(f"input_n = {payload.get('input_n')}")
                print(f"requested_mode = {payload.get('requested_mode')}")
                print(f"effective_mode = {payload.get('effective_mode')}")
                print(f"terminal_outcome = {payload.get('terminal_outcome')}")
                print(f"terminal_status = {terminal_state.get('terminal_status')}")
                if 'block_reason' in terminal_state:
                    print(f"block_reason = {terminal_state.get('block_reason')}")
                print(f"build_status = {final_output.get('build_status')}")
                print(f"assembly_status = {built.get('assembly_status')}")
                print(f"component_count = {built.get('component_count')}")
                print(f"artifacts_dir = {args.artifacts_dir}")

        elif args.command == "builder-from-factors":
            from pet.builder_from_factors import build_from_factors_pipeline

            payload = build_from_factors_pipeline(args.file, args.artifacts_dir)

            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
            else:
                final_output = payload.get("final_build_output", {})
                built = final_output.get("built_pet_object", {})
                print(f"input_n = {payload.get('input_n')}")
                print(f"schema = {payload.get('schema')}")
                print(f"build_status = {final_output.get('build_status')}")
                print(f"assembly_status = {built.get('assembly_status')}")
                print(f"component_count = {built.get('component_count')}")
                print(f"artifacts_dir = {args.artifacts_dir}")

        elif args.command == "builder-from-factorization":
            from pet.builder_from_factorization import build_from_factorization_pipeline

            payload = build_from_factorization_pipeline(args.file, args.artifacts_dir)

            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
            else:
                final_output = payload.get("final_build_output", {})
                built = final_output.get("built_pet_object", {})
                print(f"input_n = {payload.get('input_n')}")
                print(f"schema = {payload.get('schema')}")
                print(f"build_status = {final_output.get('build_status')}")
                print(f"assembly_status = {built.get('assembly_status')}")
                print(f"component_count = {built.get('component_count')}")
                print(f"artifacts_dir = {args.artifacts_dir}")

        elif args.command == "build-from-int":
            partial_report = None

            try:
                report = _build_from_int_report(args.n)
            except (ValueError, RuntimeError) as exc:
                if not args.allow_non_canonical_support:
                    raise

                msg = str(exc)
                if (
                    "build-from-int requires NEW-canonical support starting at prime 2" not in msg
                    and "integer factor support is not NEW-canonical:" not in msg
                    and "builder ended at " not in msg
                ):
                    raise

                generator_n = shape_generator(args.n)
                phase1 = _build_from_int_report(generator_n)
                partial_report = {
                    "schema": "pet-build-from-int-v2",
                    "input_n": args.n,
                    "factors": tuple(prime_factorization(args.n)),
                    "target_generator": generator_n,
                    "mode": "canonical-build+support-realization",
                    "build_status": "partial",
                    "phase1": {
                        "status": "ok",
                        "target_n": phase1["target_n"],
                        "target_generator": phase1["target_generator"],
                        "steps": phase1["steps"],
                        "path": phase1["path"],
                    },
                    "phase2": {
                        "status": "pending",
                        "same_pet_shape": True,
                        "reached_target": False,
                        "message": "canonical shape build succeeded, but non-canonical support realization is not yet implemented",
                    },
                }

            if partial_report is not None:
                if args.json:
                    print(json.dumps(_jsonable_value(partial_report), indent=2, ensure_ascii=False))
                else:
                    print(f"input_n = {partial_report['input_n']}")
                    print(f"factorization = {_format_factorization(partial_report['factors'])}")
                    print(f"target_generator = {partial_report['target_generator']}")
                    print(f"mode = {partial_report['mode']}")
                    print(f"build_status = {partial_report['build_status']}")
                    print()
                    print("[phase 1: canonical shape build]")
                    print(f"canonical_steps = {partial_report['phase1']['steps']}")
                    for row in partial_report["phase1"]["path"]:
                        print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")
                    print()
                    print("[phase 2: non-canonical support realization]")
                    print(f"status = {partial_report['phase2']['status']}")
                    print(f"same_pet_shape = {str(partial_report['phase2']['same_pet_shape']).lower()}")
                    print(f"message = {partial_report['phase2']['message']}")
            else:
                if args.json:
                    print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
                else:
                    print(f"input_n = {report['input_n']}")
                    print(f"factors = {_format_factorization(report['factors'])}")
                    print(f"target_n = {report['target_n']}")
                    print(f"target_generator = {report['target_generator']}")
                    print(f"steps = {report['steps']}")
                    for row in report["path"]:
                        print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command == "int-from-bytes":
            report = _read_int_from_bytes_file(
                args.file,
                byteorder=args.byteorder,
                signed=args.signed,
            )

            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"file = {report['file']}")
                print(f"byteorder = {report['byteorder']}")
                print(f"signed = {'yes' if report['signed'] else 'no'}")
                print(f"byte_count = {report['byte_count']}")
                print(f"hex = {report['hex']}")
                print(f"int = {report['int']}")

        elif args.command == "build-from-factors":
            factors = _parse_factor_spec_file(args.file)
            report = _build_from_factors_report(factors)

            if args.json:
                print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
            else:
                print(f"factors = {_format_factorization(report['factors'])}")
                print(f"target_n = {report['target_n']}")
                print(f"target_generator = {report['target_generator']}")
                print(f"steps = {report['steps']}")
                for row in report["path"]:
                    print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")


        elif args.command == "branch-neighbors":
            if args.n < 2:
                raise ValueError("branch-neighbors expects integers >= 2")

            rows = _sorted_plan_neighbors(args.n)

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "count": len(rows),
                    "path": _jsonable_value(rows),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"count = {len(rows)}")
                print("---")
                for row in rows:
                    print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command in {"plan-best", "branch-plan-best"}:
            if args.start < 2 or args.target < 2:
                raise ValueError("plan-best expects integers >= 2")
            if args.max_depth < 0:
                raise ValueError("--max-depth must be >= 0")
            if args.max_visited < 1:
                raise ValueError("--max-visited must be >= 1")

            path = _plan_path_best_first(
                args.start,
                args.target,
                args.max_depth,
                max_visited=args.max_visited,
            )

            if args.json:
                print(json.dumps({
                    "start": args.start,
                    "target": args.target,
                    "max_depth": args.max_depth,
                    "max_visited": args.max_visited,
                    "found": path is not None,
                    "steps": None if path is None else len(path),
                    "path": [] if path is None else _jsonable_value(path),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"A = {args.start}")
                print(f"B = {args.target}")
                print(f"max_depth = {args.max_depth}")
                print(f"max_visited = {args.max_visited}")
                print("---")
                if path is None:
                    print("NO PATH FOUND")
                else:
                    print(f"steps = {len(path)}")
                    for row in path:
                        print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command in {"plan", "branch-plan"}:
            if args.start < 2 or args.target < 2:
                raise ValueError("plan expects integers >= 2")
            if args.max_depth < 0:
                raise ValueError("--max-depth must be >= 0")

            path = _plan_path(args.start, args.target, args.max_depth)

            if args.json:
                print(json.dumps({
                    "start": args.start,
                    "target": args.target,
                    "max_depth": args.max_depth,
                    "found": path is not None,
                    "steps": None if path is None else len(path),
                    "path": [] if path is None else _jsonable_value(path),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"A = {args.start}")
                print(f"B = {args.target}")
                print(f"max_depth = {args.max_depth}")
                print("---")
                if path is None:
                    print("NO PATH FOUND")
                else:
                    print(f"steps = {len(path)}")
                    for row in path:
                        print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command == "shape-of":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import pet_to_shape

            shape = pet_to_shape(encode(args.n))

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "shape": _shape_to_jsonable(shape),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"shape = {shape}")
                print("shape tree:")
                lines = draw_shape(shape, lines=[])
                for line in lines:
                    print(line)

        elif args.command == "partial-shape-report":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_completion_report,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            report = partial_shape_completion_report(
                partial,
                max_mass=args.max_mass,
                preview=args.preview,
            )

            if args.json:
                print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"is_exact = {report['is_exact']}")
                print(f"hole_count = {report['hole_count']}")
                print(f"fill_min = {report['fill_min']}")
                print(f"min_target_shape = {report['min_target_shape']}")
                print(f"min_target_gamma = {report['min_target_gamma']}")
                print(f"completion_count = {report['completion_count']}")
                print(f"per_mass_count = {report['per_mass_count']}")
                print(f"cumulative_count = {report['cumulative_count']}")
                print(f"per_mass_min_gamma = {report['per_mass_min_gamma']}")
                print(f"preview_exact_shapes = {report['preview_exact_shapes']}")
                print(f"preview_exact_gammas = {report['preview_exact_gammas']}")


        elif args.command == "partial-shape-match":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                n_matches_partial_shape,
                normalize_partial_shape,
                pet_to_shape,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            shape = pet_to_shape(encode(args.n))
            match = n_matches_partial_shape(args.n, partial)

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "partial": _jsonable_value(partial),
                    "shape": _shape_to_jsonable(shape),
                    "match": match,
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"partial = {partial}")
                print(f"shape = {shape}")
                print(f"match = {'yes' if match else 'no'}")


        elif args.command == "partial-shape-witness":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_shortest_completion_gamma,
                partial_shape_shortest_completion_pet,
                partial_shape_shortest_completion_target,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            target_shape = partial_shape_shortest_completion_target(partial)
            target_gamma = partial_shape_shortest_completion_gamma(partial)
            target_pet = partial_shape_shortest_completion_pet(partial)

            if args.json:
                print(json.dumps({
                    "partial": _jsonable_value(partial),
                    "target_shape": _jsonable_value(target_shape),
                    "target_gamma": target_gamma,
                    "target_pet": _jsonable_value(to_jsonable(target_pet)),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"partial = {partial}")
                print(f"target_shape = {target_shape}")
                print(f"target_gamma = {target_gamma}")
                print("target_pet:")
                print(to_json(target_pet))


        elif args.command == "partial-shape-completions":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_completion_frontier,
                partial_shape_completion_gamma_frontier,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            shapes = partial_shape_completion_frontier(partial, args.max_mass)
            gammas = partial_shape_completion_gamma_frontier(partial, args.max_mass)

            if args.json:
                print(json.dumps({
                    "partial": _jsonable_value(partial),
                    "max_mass": args.max_mass,
                    "count": len(shapes),
                    "exact_shapes": _jsonable_value(shapes[:args.preview]),
                    "exact_gammas": gammas[:args.preview],
                }, indent=2, ensure_ascii=False))
            else:
                print(f"partial = {partial}")
                print(f"max_mass = {args.max_mass}")
                print(f"count = {len(shapes)}")
                print(f"exact_shapes (preview={args.preview}):")
                for shape in shapes[:args.preview]:
                    print(f"  {shape}")
                print(f"exact_gammas (preview={args.preview}) = {gammas[:args.preview]}")



        elif args.command == "partial-shape-forced-core":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_change_masses,
                partial_shape_forced_core_meets_window,
                partial_shape_forced_core_report,
                partial_shape_forced_core_stabilization_mass,
                partial_shape_forced_core_stable_window,
                partial_shape_forced_core_trace,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.window < 1:
                raise ValueError("--window must be >= 1")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_forced_core_report(partial, effective_max_mass)
            trace = partial_shape_forced_core_trace(partial, effective_max_mass) if args.trace else ()
            change_masses = partial_shape_forced_core_change_masses(partial, effective_max_mass)
            stabilization_mass = partial_shape_forced_core_stabilization_mass(partial, effective_max_mass)
            stable_window = partial_shape_forced_core_stable_window(partial, effective_max_mass)
            meets_window = partial_shape_forced_core_meets_window(partial, effective_max_mass, args.window)
            auto_window_met = (
                partial_shape_forced_core_meets_window(partial, effective_max_mass, auto_window)
                if auto_window is not None else None
            )

            if args.json:
                payload = dict(report)
                if args.trace:
                    payload["trace"] = trace
                payload["change_masses"] = change_masses
                payload["stabilization_mass"] = stabilization_mass
                payload["stable_window"] = stable_window
                payload["fixed_window"] = args.window
                payload["meets_window"] = meets_window
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                payload["auto_window_met"] = auto_window_met
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"completion_count = {report['completion_count']}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"is_exact = {report['is_exact']}")
                print(f"change_masses = {change_masses}")
                print(f"stable_window = {stable_window}")
                if stable_window < 2:
                    print("warning = weak-stabilization")
                print(f"fixed_window = {args.window}")
                print(f"meets_window = {'yes' if meets_window else 'no'}")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                    print(f"auto_window_met = {'yes' if auto_window_met else 'no'}")
                if args.trace:
                    print("trace:")
                    for row in trace:
                        delta = "Δ" if row["changed"] else "="
                        print(
                            "  ",
                            f"{delta}[{row['change_kind']}]",
                            f"max_mass={row['max_mass']}",
                            f"completion_count={row['completion_count']}",
                            f"prev={row['prev_forced_core']}",
                            f"forced_core={row['forced_core']}",
                        )
                    if stabilization_mass is None:
                        print("stabilization_mass (inspected suffix) = none")
                    else:
                        print(f"stabilization_mass (inspected suffix) = {stabilization_mass}")


        elif args.command == "partial-shape-residual":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual(partial, effective_max_mass)

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"stable_window = {report['stable_window']}")
                print(f"stabilization_mass = {report['stabilization_mass']}")
                if report["stable_window"] < 2:
                    print("warning = weak-stabilization")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")


        elif args.command == "partial-shape-residual-profile":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual_profile,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual_profile(partial, effective_max_mass, preview=args.preview)

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                print("per_path:")
                for path, row in report["per_path"].items():
                    print(f"  path = {path}")
                    print(f"    count = {row['count']}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    preview_shapes = {row['preview_shapes']}")
                    print(f"    preview_local_gammas = {row['preview_local_gammas']}")


        elif args.command == "partial-shape-residual-summary":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual_summary,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual_summary(
                partial,
                effective_max_mass,
                preview=args.preview,
                fast_preview=args.fast_preview,
            )

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"stable_window = {report['stable_window']}")
                print(f"stabilization_mass = {report['stabilization_mass']}")
                if report["stable_window"] < 2:
                    print("warning = weak-stabilization")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                print("per_path_summary:")
                for path, row in report["per_path_summary"].items():
                    print(f"  path = {path}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    observed_local_count = {row['observed_local_count']}")
                    print(f"    observed_local_shapes = {row['observed_local_shapes']}")
                    print(f"    observed_local_gammas = {row['observed_local_gammas']}")


        elif args.command == "partial-shape-target":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_observed_decomposition,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_observed_decomposition(
                partial,
                max_mass=effective_max_mass,
                preview=args.preview,
                fast_preview=args.fast_preview,
            )

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"observed_core = {report['observed_core']}")
                print(f"observed_core_kind = {report['observed_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"residual_free_paths = {report['residual_free_paths']}")
                print(f"residual_free_path_count = {report['residual_free_path_count']}")
                print("evidence:")
                print(f"  max_mass = {report['evidence']['max_mass']}")
                print(f"  stable_window = {report['evidence']['stable_window']}")
                print(f"  stabilization_mass = {report['evidence']['stabilization_mass']}")
                if report["evidence"]["stable_window"] < 2:
                    print("  warning = weak-stabilization")
                print(f"  forced_hole_count = {report['evidence']['forced_hole_count']}")
                print(f"  fast_preview = {'yes' if report['evidence']['fast_preview'] else 'no'}")
                if auto_window is not None:
                    print(f"  auto_window = {auto_window}")
                    print(f"  max_mass_cap = {args.max_mass_cap}")
                    print(f"  effective_max_mass = {effective_max_mass}")
                print("residual_local_profiles:")
                for path, row in report["residual_local_profiles"].items():
                    print(f"  path = {path}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    observed_local_count = {row['observed_local_count']}")
                    print(f"    observed_local_shapes = {row['observed_local_shapes']}")
                    print(f"    observed_local_gammas = {row['observed_local_gammas']}")

        elif args.command == "rewrite":
            from pet import rewrite_metric as _rewrite_metric

            if args.rewrite_command == "pair":
                return _rewrite_metric.cmd_pair(args)
            elif args.rewrite_command == "scan":
                return _rewrite_metric.cmd_scan(args)
            elif args.rewrite_command == "matrix":
                return _rewrite_metric.cmd_matrix(args)
            raise ValueError(f"unknown rewrite command: {args.rewrite_command}")

        elif args.command == "query":
            return run_query(args)

        elif args.command == "families":
            return run_families(args)

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()

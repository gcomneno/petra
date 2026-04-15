#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, deque
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Edge:
    src: int
    dst: int
    label: str
    cost: int = 1


@dataclass(frozen=True)
class PathStep:
    src: int
    dst: int
    label: str


def _json_dump(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# REPO ADAPTER: ADATTA QUI
# ---------------------------------------------------------------------------

def _raw_edges_for_number(n: int) -> list[dict[str, Any]]:
    if n < 2:
        return []

    # Import lazy per evitare dipendenze premature.
    # Per ora l'adapter resta agganciato a pet.cli.
    from pet.cli import _pathwise_edges_for_number

    return _pathwise_edges_for_number(n)


def pet_rewrite_neighbors(n: int, *, overscan: int | None = None) -> list[Edge]:
    """
    Wrapper robusto che normalizza l'output dell'adapter in Edge.
    """
    raw = _raw_edges_for_number(n)
    out: list[Edge] = []

    for item in raw:
        if not isinstance(item, dict):
            raise TypeError(f"Edge raw non dict per n={n}: {item!r}")

        dst = item.get("to", item.get("target", item.get("target_n")))
        label = item.get("label", item.get("move"))

        if not isinstance(dst, int):
            raise TypeError(f"Target invalido per n={n}: {item!r}")
        if not isinstance(label, str):
            raise TypeError(f"Label invalida per n={n}: {item!r}")

        if overscan is not None and not (1 <= dst <= overscan):
            # taglio prudente del grafo osservato
            continue

        out.append(Edge(src=n, dst=dst, label=label, cost=1))

    # Tie-break canonico locale:
    # 1) label lessicografica
    # 2) target crescente
    out.sort(key=lambda e: (e.label, e.dst))
    return out


# ---------------------------------------------------------------------------
# GRAFO
# ---------------------------------------------------------------------------

def build_graph(*, overscan: int) -> dict[int, list[Edge]]:
    graph: dict[int, list[Edge]] = {}
    for n in range(1, overscan + 1):
        graph[n] = pet_rewrite_neighbors(n, overscan=overscan)
    return graph


def graph_stats(graph: dict[int, list[Edge]], *, overscan: int) -> dict[str, Any]:
    total_edges = sum(len(edges) for edges in graph.values())
    active_nodes = sum(1 for edges in graph.values() if edges)
    label_counts = Counter(edge.label for edges in graph.values() for edge in edges)

    out_of_domain = 0
    for edges in graph.values():
        for edge in edges:
            if not (1 <= edge.dst <= overscan):
                out_of_domain += 1

    return {
        "overscan": overscan,
        "node_count": len(graph),
        "active_node_count": active_nodes,
        "edge_count": total_edges,
        "distinct_label_count": len(label_counts),
        "label_counts": dict(sorted(label_counts.items())),
        "out_of_domain_edges_seen_after_filter": out_of_domain,
    }


# ---------------------------------------------------------------------------
# BFS / DISTANZA / DIFFERENZA CANONICA
# ---------------------------------------------------------------------------

def bfs_shortest_path(
    graph: dict[int, list[Edge]],
    *,
    src: int,
    dst: int,
) -> tuple[int | None, list[PathStep]]:
    """
    Shortest path a costo unitario.
    Grazie all'ordinamento dei vicini, il primo shortest path trovato
    è il canonico secondo il tie-break locale.
    """
    if src == dst:
        return 0, []

    if src not in graph or dst not in graph:
        return None, []

    queue = deque([src])
    seen = {src}
    parent: dict[int, tuple[int, str]] = {}

    while queue:
        cur = queue.popleft()
        for edge in graph[cur]:
            nxt = edge.dst
            if nxt in seen:
                continue
            seen.add(nxt)
            parent[nxt] = (cur, edge.label)
            if nxt == dst:
                path = _reconstruct_path(parent, src=src, dst=dst)
                return len(path), path
            queue.append(nxt)

    return None, []


def bfs_all_distances(
    graph: dict[int, list[Edge]],
    *,
    src: int,
) -> dict[int, int]:
    dist = {src: 0}
    queue = deque([src])

    while queue:
        cur = queue.popleft()
        for edge in graph[cur]:
            nxt = edge.dst
            if nxt in dist:
                continue
            dist[nxt] = dist[cur] + 1
            queue.append(nxt)

    return dist


def _reconstruct_path(
    parent: dict[int, tuple[int, str]],
    *,
    src: int,
    dst: int,
) -> list[PathStep]:
    cur = dst
    rev: list[PathStep] = []

    while cur != src:
        prev, label = parent[cur]
        rev.append(PathStep(src=prev, dst=cur, label=label))
        cur = prev

    rev.reverse()
    return rev


def pet_rewrite_distance(
    graph: dict[int, list[Edge]],
    *,
    src: int,
    dst: int,
) -> int | None:
    distance, _ = bfs_shortest_path(graph, src=src, dst=dst)
    return distance


def pet_rewrite_difference(
    graph: dict[int, list[Edge]],
    *,
    src: int,
    dst: int,
) -> dict[str, Any]:
    distance, path = bfs_shortest_path(graph, src=src, dst=dst)
    return {
        "src": src,
        "dst": dst,
        "reachable": distance is not None,
        "cost": distance,
        "path": [asdict(step) for step in path],
    }


# ---------------------------------------------------------------------------
# SCAN
# ---------------------------------------------------------------------------

def scan_pairs(
    graph: dict[int, list[Edge]],
    *,
    n_max: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for src in range(1, n_max + 1):
        distances = bfs_all_distances(graph, src=src)
        for dst in range(1, n_max + 1):
            d = distances.get(dst)
            rows.append(
                {
                    "src": src,
                    "dst": dst,
                    "reachable": d is not None,
                    "pet_distance": d,
                    "numeric_distance": abs(src - dst),
                    "distance_gap": None if d is None else d - abs(src - dst),
                }
            )
    return rows


def scan_hubs(
    graph: dict[int, list[Edge]],
    *,
    n_max: int,
) -> list[dict[str, Any]]:
    """
    Conta quante volte un nodo compare come nodo interno
    di un cammino canonico minimo tra coppie in 1..n_max.
    """
    hub_counter: Counter[int] = Counter()

    for src in range(1, n_max + 1):
        for dst in range(1, n_max + 1):
            if src == dst:
                continue
            _, path = bfs_shortest_path(graph, src=src, dst=dst)
            if not path:
                continue

            internal_nodes = [step.dst for step in path[:-1]]
            for node in internal_nodes:
                if 1 <= node <= n_max:
                    hub_counter[node] += 1

    return [
        {"node": node, "hub_score": score}
        for node, score in hub_counter.most_common()
    ]


def pick_surprises(rows: list[dict[str, Any]], *, limit: int = 10) -> dict[str, Any]:
    reachable = [row for row in rows if row["reachable"] and row["src"] != row["dst"]]
    unreachable = [row for row in rows if not row["reachable"] and row["src"] != row["dst"]]

    high_gap = sorted(
        reachable,
        key=lambda row: (row["distance_gap"], row["pet_distance"], row["src"], row["dst"]),
        reverse=True,
    )[:limit]

    low_gap = sorted(
        reachable,
        key=lambda row: (row["distance_gap"], row["pet_distance"], row["src"], row["dst"]),
    )[:limit]

    return {
        "largest_positive_gap": high_gap,
        "largest_negative_gap": low_gap,
        "sample_unreachable": unreachable[:limit],
    }


def pick_asymmetries(rows: list[dict[str, Any]], *, n_max: int, limit: int = 10) -> list[dict[str, Any]]:
    by_pair = {
        (row["src"], row["dst"]): row
        for row in rows
        if row["reachable"]
    }

    out: list[dict[str, Any]] = []
    for a in range(1, n_max + 1):
        for b in range(a + 1, n_max + 1):
            ab = by_pair.get((a, b))
            ba = by_pair.get((b, a))
            if ab is None or ba is None:
                continue

            d_ab = ab["pet_distance"]
            d_ba = ba["pet_distance"]
            asym = d_ab - d_ba

            out.append(
                {
                    "a": a,
                    "b": b,
                    "d_ab": d_ab,
                    "d_ba": d_ba,
                    "asymmetry": asym,
                    "abs_asymmetry": abs(asym),
                }
            )

    out.sort(
        key=lambda row: (
            row["abs_asymmetry"],
            row["asymmetry"],
            -row["a"],
            -row["b"],
        ),
        reverse=True,
    )
    return out[:limit]


def _prime_from_label(label: str) -> int | None:
    m = re.search(r"p=(\d+)", label)
    if m:
        return int(m.group(1))
    m = re.search(r"x(\d+)", label)
    if m:
        return int(m.group(1))
    return None


def pick_attractors(
    rows: list[dict[str, Any]],
    *,
    n_max: int,
    limit: int = 10,
    min_incoming: int = 5,
    min_outgoing: int = 5,
) -> list[dict[str, Any]]:
    incoming: dict[int, list[int]] = {n: [] for n in range(2, n_max + 1)}
    outgoing: dict[int, list[int]] = {n: [] for n in range(2, n_max + 1)}

    for row in rows:
        src = row["src"]
        dst = row["dst"]
        d = row["pet_distance"]
        if not row["reachable"]:
            continue
        if src == dst:
            continue
        if not (2 <= src <= n_max and 2 <= dst <= n_max):
            continue
        incoming[dst].append(d)
        outgoing[src].append(d)

    out: list[dict[str, Any]] = []
    for n in range(2, n_max + 1):
        inc = incoming[n]
        outg = outgoing[n]
        if len(inc) < min_incoming or len(outg) < min_outgoing:
            continue

        avg_in = sum(inc) / len(inc)
        avg_out = sum(outg) / len(outg)
        score = avg_out - avg_in

        out.append(
            {
                "node": n,
                "incoming_count": len(inc),
                "outgoing_count": len(outg),
                "avg_in": round(avg_in, 3),
                "avg_out": round(avg_out, 3),
                "attractor_score": round(score, 3),
            }
        )

    out.sort(
        key=lambda row: (
            row["attractor_score"],
            row["incoming_count"],
            -row["avg_in"],
            row["node"],
        ),
        reverse=True,
    )
    return out[:limit]


def family_report(
    rows: list[dict[str, Any]],
    *,
    n_max: int,
    primes: tuple[int, ...] = (2, 3, 5),
) -> dict[str, list[dict[str, Any]]]:
    incoming: dict[int, list[int]] = {n: [] for n in range(2, n_max + 1)}
    outgoing: dict[int, list[int]] = {n: [] for n in range(2, n_max + 1)}

    for row in rows:
        src = row["src"]
        dst = row["dst"]
        d = row["pet_distance"]
        if not row["reachable"]:
            continue
        if src == dst:
            continue
        if not (2 <= src <= n_max and 2 <= dst <= n_max):
            continue
        incoming[dst].append(d)
        outgoing[src].append(d)

    out: dict[str, list[dict[str, Any]]] = {}
    for p in primes:
        fam: list[dict[str, Any]] = []
        value = p
        exp = 1
        while value <= n_max:
            inc = incoming.get(value, [])
            outg = outgoing.get(value, [])
            avg_in = round(sum(inc) / len(inc), 3) if inc else None
            avg_out = round(sum(outg) / len(outg), 3) if outg else None
            score = None
            if avg_in is not None and avg_out is not None:
                score = round(avg_out - avg_in, 3)

            fam.append(
                {
                    "node": value,
                    "prime": p,
                    "exp": exp,
                    "incoming_count": len(inc),
                    "outgoing_count": len(outg),
                    "avg_in": avg_in,
                    "avg_out": avg_out,
                    "attractor_score": score,
                }
            )
            value *= p
            exp += 1

        out[f"p={p}"] = fam

    return out


def one_step_return_costs(
    graph: dict[int, list[Edge]],
    *,
    n_max: int,
    limit: int = 10,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    label_stats: dict[str, list[int]] = {}
    prime_stats: dict[int, list[int]] = {}

    for src in range(2, n_max + 1):
        for edge in graph.get(src, []):
            dst = edge.dst
            if not (2 <= dst <= n_max):
                continue

            back_cost, back_path = bfs_shortest_path(graph, src=dst, dst=src)
            rows.append(
                {
                    "src": src,
                    "dst": dst,
                    "forward_label": edge.label,
                    "back_cost": back_cost,
                    "back_path": [asdict(step) for step in back_path],
                }
            )
            if back_cost is not None:
                label_stats.setdefault(edge.label, []).append(back_cost)
                prime = _prime_from_label(edge.label)
                if prime is not None:
                    prime_stats.setdefault(prime, []).append(back_cost)

    hardest = sorted(
        rows,
        key=lambda row: (
            -999 if row["back_cost"] is None else row["back_cost"],
            row["forward_label"],
            row["src"],
            row["dst"],
        ),
        reverse=True,
    )[:limit]

    by_label = []
    for label, costs in sorted(label_stats.items()):
        by_label.append(
            {
                "label": label,
                "count": len(costs),
                "min_back_cost": min(costs),
                "max_back_cost": max(costs),
                "avg_back_cost": round(sum(costs) / len(costs), 3),
            }
        )

    by_prime = []
    for prime, costs in sorted(prime_stats.items()):
        by_prime.append(
            {
                "prime": prime,
                "count": len(costs),
                "min_back_cost": min(costs),
                "max_back_cost": max(costs),
                "avg_back_cost": round(sum(costs) / len(costs), 3),
            }
        )

    return {
        "hardest_returns": hardest,
        "by_label": by_label,
        "by_prime": by_prime,
    }


def compose_transport_v1(
    graph: dict[int, list[Edge]],
    *,
    a: int,
    b: int,
    c: int,
) -> dict[str, Any]:
    """
    A-v1:
    - witness sintattico = concatenazione di T(a,b) e T(b,c)
    - risultato semantico = T(a,c)
    """
    ab = pet_rewrite_difference(graph, src=a, dst=b)
    bc = pet_rewrite_difference(graph, src=b, dst=c)
    ac = pet_rewrite_difference(graph, src=a, dst=c)

    compatible = (
        ab["reachable"]
        and bc["reachable"]
        and ab["dst"] == bc["src"] == b
    )

    witness_path = ((ab["path"] or []) + (bc["path"] or [])) if compatible else []

    return {
        "a": a,
        "b": b,
        "c": c,
        "compatible": compatible,
        "witness_path": witness_path,
        "witness_cost": len(witness_path) if compatible else None,
        "result_reachable": ac["reachable"],
        "result_path": ac["path"],
        "result_cost": ac["cost"],
        "witness_equals_result": compatible and witness_path == (ac["path"] or []),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_pair(args: argparse.Namespace) -> int:
    graph = build_graph(overscan=args.overscan)
    result = pet_rewrite_difference(graph, src=args.src, dst=args.dst)

    if args.json:
        print(_json_dump(result))
        return 0

    print(f"src = {args.src}")
    print(f"dst = {args.dst}")
    print(f"reachable = {result['reachable']}")
    print(f"cost = {result['cost']}")

    path = result["path"]
    if not path:
        print("path = []")
        return 0

    print("path:")
    for step in path:
        print(f"  {step['src']} --{step['label']}--> {step['dst']}")
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    graph = build_graph(overscan=args.overscan)
    rows = scan_pairs(graph, n_max=args.n_max)

    payload = {
        "n_max": args.n_max,
        "overscan": args.overscan,
        "stats": graph_stats(graph, overscan=args.overscan),
        "distances": rows,
    }

    print(_json_dump(payload))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    graph = build_graph(overscan=args.overscan)
    stats = graph_stats(graph, overscan=args.overscan)
    rows = scan_pairs(graph, n_max=args.n_max)
    hubs = scan_hubs(graph, n_max=args.n_max)
    surprises = pick_surprises(rows, limit=args.limit)
    asymmetries = pick_asymmetries(rows, n_max=args.n_max, limit=args.limit)
    attractors = pick_attractors(rows, n_max=args.n_max, limit=args.limit, min_incoming=5, min_outgoing=5)
    families = family_report(rows, n_max=args.n_max, primes=(2, 3, 5, 7))
    one_step = one_step_return_costs(graph, n_max=args.n_max, limit=args.limit)

    payload = {
        "n_max": args.n_max,
        "overscan": args.overscan,
        "stats": stats,
        "surprises": surprises,
        "top_hubs": hubs[: args.limit],
        "top_asymmetries": asymmetries,
        "top_attractors": attractors,
        "family_report": families,
        "one_step_return_costs": one_step,
    }

    if args.json:
        print(_json_dump(payload))
        return 0

    print("stats:")
    for key, value in payload["stats"].items():
        if key == "label_counts":
            continue
        print(f"  {key} = {value}")

    print("\nlabel_counts:")
    for label, count in payload["stats"]["label_counts"].items():
        print(f"  {label}: {count}")

    print("\ntop_hubs:")
    for row in payload["top_hubs"]:
        print(f"  n={row['node']} hub_score={row['hub_score']}")

    print("\nlargest_positive_gap:")
    for row in payload["surprises"]["largest_positive_gap"]:
        print(
            f"  {row['src']} -> {row['dst']}: "
            f"pet={row['pet_distance']} num={row['numeric_distance']} "
            f"gap={row['distance_gap']}"
        )

    print("\nlargest_negative_gap:")
    for row in payload["surprises"]["largest_negative_gap"]:
        print(
            f"  {row['src']} -> {row['dst']}: "
            f"pet={row['pet_distance']} num={row['numeric_distance']} "
            f"gap={row['distance_gap']}"
        )

    print("\ntop_asymmetries:")
    for row in payload["top_asymmetries"]:
        print(
            f"  {row['a']} <-> {row['b']}: "
            f"d({row['a']},{row['b']})={row['d_ab']} "
            f"d({row['b']},{row['a']})={row['d_ba']} "
            f"delta={row['asymmetry']}"
        )

    print("\ntop_attractors:")
    for row in payload["top_attractors"]:
        print(
            f"  n={row['node']}: "
            f"avg_in={row['avg_in']} avg_out={row['avg_out']} "
            f"score={row['attractor_score']} "
            f"in={row['incoming_count']} out={row['outgoing_count']}"
        )

    print("\nfamily_report:")
    for family_name, family_rows in payload["family_report"].items():
        print(f"  {family_name}:")
        for row in family_rows:
            print(
                f"    n={row['node']} ({row['prime']}^{row['exp']}): "
                f"avg_in={row['avg_in']} avg_out={row['avg_out']} "
                f"score={row['attractor_score']} "
                f"in={row['incoming_count']} out={row['outgoing_count']}"
            )

    dyadic_rows = payload["family_report"].get("p=2", [])
    print("\ndyadic_trend:")
    prev_score = None
    for row in dyadic_rows:
        score = row["attractor_score"]
        delta = None if prev_score is None or score is None else round(score - prev_score, 3)
        print(
            f"  n={row['node']}: "
            f"score={score} "
            f"delta_from_prev={delta} "
            f"avg_in={row['avg_in']} avg_out={row['avg_out']}"
        )
        prev_score = score

    print("\none_step_return_costs.by_label:")
    for row in payload["one_step_return_costs"]["by_label"]:
        print(
            f"  {row['label']}: "
            f"count={row['count']} min={row['min_back_cost']} "
            f"max={row['max_back_cost']} avg={row['avg_back_cost']}"
        )

    print("\none_step_return_costs.by_prime:")
    for row in payload["one_step_return_costs"]["by_prime"]:
        print(
            f"  p={row['prime']}: "
            f"count={row['count']} min={row['min_back_cost']} "
            f"max={row['max_back_cost']} avg={row['avg_back_cost']}"
        )

    print("\none_step_return_costs.hardest_returns:")
    for row in payload["one_step_return_costs"]["hardest_returns"]:
        print(
            f"  {row['src']} --{row['forward_label']}--> {row['dst']}: "
            f"return_cost={row['back_cost']}"
        )

    if payload["surprises"]["sample_unreachable"]:
        print("\nsample_unreachable:")
        for row in payload["surprises"]["sample_unreachable"]:
            print(f"  {row['src']} -> {row['dst']}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PET rewrite metric: neighbors, distance, canonical difference."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pair = sub.add_parser("pair", help="Compute canonical rewrite difference between two numbers.")
    p_pair.add_argument("src", type=int)
    p_pair.add_argument("dst", type=int)
    p_pair.add_argument("--overscan", type=int, default=90)
    p_pair.add_argument("--json", action="store_true")
    p_pair.set_defaults(func=cmd_pair)

    p_scan = sub.add_parser("scan", help="Global scan over 1..N with overscan.")
    p_scan.add_argument("--n-max", type=int, default=30)
    p_scan.add_argument("--overscan", type=int, default=90)
    p_scan.add_argument("--limit", type=int, default=10)
    p_scan.add_argument("--json", action="store_true")
    p_scan.set_defaults(func=cmd_scan)

    p_matrix = sub.add_parser("matrix", help="Emit all pair distances as JSON.")
    p_matrix.add_argument("--n-max", type=int, default=30)
    p_matrix.add_argument("--overscan", type=int, default=90)
    p_matrix.add_argument("--json", action="store_true", default=True)
    p_matrix.set_defaults(func=cmd_matrix)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

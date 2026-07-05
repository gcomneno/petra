#!/usr/bin/env python3
"""Targeted PET-METICA probe for the 7 × {2^k, 3^k} family at tier 300.

Runs a bounded rewrite scan and analyzes asymmetric pairs involving family
members, with emphasis on canonical seed pairs (2^k, 7·2^k) and (3^k, 7·3^k).

All findings are descriptive and bounded — not theorems.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[2]
src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from pet.rewrite_metric import (  # noqa: E402
    build_graph,
    graph_stats,
    scan_hubs,
    scan_pairs,
)

DEFAULT_N_MAX = 300
DEFAULT_OVERSCAN = 900


def seven_family_members(n_max: int) -> dict[str, list[int]]:
    dyadic: list[int] = []
    k = 0
    while True:
        value = 7 * (2**k)
        if value > n_max:
            break
        dyadic.append(value)
        k += 1

    triadic: list[int] = []
    k = 0
    while True:
        value = 7 * (3**k)
        if value > n_max:
            break
        triadic.append(value)
        k += 1

    return {
        "dyadic": dyadic,
        "triadic": triadic,
        "all": sorted(set(dyadic + triadic)),
    }


def canonical_seed_pairs(n_max: int) -> dict[str, list[dict[str, int]]]:
    dyadic_pairs: list[dict[str, int]] = []
    k = 0
    while True:
        base = 2**k
        target = 7 * base
        if target > n_max:
            break
        dyadic_pairs.append({"base": base, "target": target, "k": k})
        k += 1

    triadic_pairs: list[dict[str, int]] = []
    k = 0
    while True:
        base = 3**k
        target = 7 * base
        if target > n_max:
            break
        triadic_pairs.append({"base": base, "target": target, "k": k})
        k += 1

    return {"dyadic_seeds": dyadic_pairs, "triadic_seeds": triadic_pairs}


def _pair_lookup(rows: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    return {(row["src"], row["dst"]): row for row in rows}


def _asymmetry_row(
    lookup: dict[tuple[int, int], dict[str, Any]],
    *,
    a: int,
    b: int,
) -> dict[str, Any] | None:
    ab = lookup.get((a, b))
    ba = lookup.get((b, a))
    if ab is None or ba is None or not ab["reachable"] or not ba["reachable"]:
        return None

    d_ab = ab["pet_distance"]
    d_ba = ba["pet_distance"]
    return {
        "a": a,
        "b": b,
        "d_ab": d_ab,
        "d_ba": d_ba,
        "asymmetry": d_ab - d_ba,
        "abs_asymmetry": abs(d_ab - d_ba),
    }


def _directional_costs(
    lookup: dict[tuple[int, int], dict[str, Any]],
    *,
    base: int,
    target: int,
) -> dict[str, Any]:
    forward = lookup.get((base, target))
    reverse = lookup.get((target, base))
    forward_ok = forward is not None and forward["reachable"]
    reverse_ok = reverse is not None and reverse["reachable"]

    d_forward = forward["pet_distance"] if forward_ok else None
    d_reverse = reverse["pet_distance"] if reverse_ok else None
    asymmetry = None
    if forward_ok and reverse_ok:
        asymmetry = d_forward - d_reverse

    return {
        "base": base,
        "target": target,
        "d_base_to_target": d_forward,
        "d_target_to_base": d_reverse,
        "forward_reachable": forward_ok,
        "reverse_reachable": reverse_ok,
        "asymmetry": asymmetry,
        "abs_asymmetry": None if asymmetry is None else abs(asymmetry),
    }


def analyze_canonical_seeds(
    lookup: dict[tuple[int, int], dict[str, Any]],
    *,
    n_max: int,
) -> dict[str, Any]:
    seeds = canonical_seed_pairs(n_max)
    dyadic_rows: list[dict[str, Any]] = []
    triadic_rows: list[dict[str, Any]] = []

    for seed in seeds["dyadic_seeds"]:
        row = _directional_costs(lookup, base=seed["base"], target=seed["target"])
        if row["forward_reachable"] or row["reverse_reachable"]:
            row["k"] = seed["k"]
            row["family"] = "7·2^k"
            dyadic_rows.append(row)

    for seed in seeds["triadic_seeds"]:
        row = _directional_costs(lookup, base=seed["base"], target=seed["target"])
        if row["forward_reachable"] or row["reverse_reachable"]:
            row["k"] = seed["k"]
            row["family"] = "7·3^k"
            triadic_rows.append(row)

    return {
        "dyadic_seeds": dyadic_rows,
        "triadic_seeds": triadic_rows,
    }


def family_partner_asymmetries(
    lookup: dict[tuple[int, int], dict[str, Any]],
    *,
    family: set[int],
    n_max: int,
    min_abs_asymmetry: int,
    limit: int,
) -> list[dict[str, Any]]:
    seen: set[tuple[int, int]] = set()
    out: list[dict[str, Any]] = []

    for member in sorted(family):
        for partner in range(2, n_max + 1):
            if partner == member:
                continue
            a, b = sorted((member, partner))
            if (a, b) in seen:
                continue
            row = _asymmetry_row(lookup, a=a, b=b)
            if row is None:
                continue
            if row["abs_asymmetry"] < min_abs_asymmetry:
                continue
            seen.add((a, b))
            row = dict(row)
            row["family_member"] = member
            row["partner"] = partner
            out.append(row)

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


def family_hub_scores(
    hubs: list[dict[str, Any]],
    *,
    family: set[int],
) -> list[dict[str, Any]]:
    score_by_node = {row["node"]: row["hub_score"] for row in hubs}
    return [
        {"node": node, "hub_score": score_by_node.get(node, 0)}
        for node in sorted(family)
    ]


def run_probe(
    *,
    n_max: int,
    overscan: int,
    min_abs_asymmetry: int,
    partner_limit: int,
) -> dict[str, Any]:
    graph = build_graph(overscan=overscan)
    rows = scan_pairs(graph, n_max=n_max)
    hubs = scan_hubs(graph, n_max=n_max)
    lookup = _pair_lookup(rows)

    members = seven_family_members(n_max)
    family_set = set(members["all"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_max": n_max,
        "overscan": overscan,
        "min_abs_asymmetry": min_abs_asymmetry,
        "family_members": members,
        "stats": graph_stats(graph, overscan=overscan),
        "family_hub_scores": family_hub_scores(hubs, family=family_set),
        "canonical_seed_asymmetries": analyze_canonical_seeds(lookup, n_max=n_max),
        "family_partner_asymmetries": family_partner_asymmetries(
            lookup,
            family=family_set,
            n_max=n_max,
            min_abs_asymmetry=min_abs_asymmetry,
            limit=partner_limit,
        ),
    }


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(payload: dict[str, Any], *, json_path: str, md_path: str) -> str:
    members = payload["family_members"]
    seeds = payload["canonical_seed_asymmetries"]
    n_max = payload["n_max"]

    lines = [
        f"# PET-METICA seven-family probe (tier {n_max})",
        "",
        "Targeted bounded scan for the family `7 × {2^k, 3^k}` within `1..n_max`.",
        "",
        "## Scope",
        "",
        f"- generated at (UTC): `{payload['generated_at']}`",
        f"- n_max: `{payload['n_max']}`",
        f"- overscan: `{payload['overscan']}`",
        f"- min |asymmetry| for partner table: `{payload['min_abs_asymmetry']}`",
        f"- dyadic family members: `{members['dyadic']}`",
        f"- triadic family members: `{members['triadic']}`",
        "- reproduction command:",
        "",
        f"    tools/research/pet_metica_seven_family_probe.py \\",
        f"      --n-max {n_max} --overscan {payload['overscan']} \\",
        f"      --output-json {json_path} \\",
        f"      --output-md {md_path}",
        "",
        "## Observations",
        "",
        "### Family hub scores",
        "",
        _md_table(
            ["node", "hub_score"],
            [[row["node"], row["hub_score"]] for row in payload["family_hub_scores"]],
        ),
        "",
        "### Canonical seed pairs `(2^k, 7·2^k)`",
        "",
        _md_table(
            ["k", "base", "target", "d(base→target)", "d(target→base)", "asymmetry"],
            [
                [
                    row["k"],
                    row["base"],
                    row["target"],
                    row["d_base_to_target"],
                    row["d_target_to_base"],
                    row["asymmetry"],
                ]
                for row in seeds["dyadic_seeds"]
            ],
        )
        if seeds["dyadic_seeds"]
        else "_No dyadic seed pairs in range._",
        "",
        "### Canonical seed pairs `(3^k, 7·3^k)`",
        "",
        _md_table(
            ["k", "base", "target", "d(base→target)", "d(target→base)", "asymmetry"],
            [
                [
                    row["k"],
                    row["base"],
                    row["target"],
                    row["d_base_to_target"],
                    row["d_target_to_base"],
                    row["asymmetry"],
                ]
                for row in seeds["triadic_seeds"]
            ],
        )
        if seeds["triadic_seeds"]
        else "_No triadic seed pairs in range._",
        "",
        "### Strong family-involved asymmetric pairs",
        "",
        _md_table(
            ["family_member", "partner", "d_ab", "d_ba", "asymmetry"],
            [
                [
                    row["family_member"],
                    row["partner"],
                    row["d_ab"],
                    row["d_ba"],
                    row["asymmetry"],
                ]
                for row in payload["family_partner_asymmetries"]
            ],
        )
        if payload["family_partner_asymmetries"]
        else "_None above threshold._",
        "",
        "## Interpretation and limits",
        "",
        "1. Family members and seed pairs are defined algebraically inside the",
        "   bounded window `1..n_max`; this is not an infinite-family theorem.",
        "2. Canonical seeds test the `(base, 7·base)` pattern for bases `2^k` and",
        "   `3^k` separately.",
        "3. Partner tables list strong asymmetries where at least one endpoint is",
        "   a family member.",
        "",
        "## Non-claims",
        "",
        "This probe does not claim global asymmetry laws for all multiples of 7,",
        "asymptotic hub rank for the family, or invariance under overscan choice.",
        "",
    ]

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Targeted PET-METICA probe for 7 × {2^k, 3^k} at tier 300.",
    )
    parser.add_argument("--n-max", type=int, default=DEFAULT_N_MAX)
    parser.add_argument("--overscan", type=int, default=DEFAULT_OVERSCAN)
    parser.add_argument("--min-abs-asymmetry", type=int, default=6)
    parser.add_argument("--partner-limit", type=int, default=20)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    payload = run_probe(
        n_max=args.n_max,
        overscan=args.overscan,
        min_abs_asymmetry=args.min_abs_asymmetry,
        partner_limit=args.partner_limit,
    )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        json_ref = args.output_json or Path(
            f"docs/reports/data/metica-seven-family-{args.n_max}.json"
        )
        args.output_md.write_text(
            render_markdown(
                payload,
                json_path=str(json_ref),
                md_path=str(args.output_md),
            ),
            encoding="utf-8",
        )

    if args.json or (not args.output_json and not args.output_md):
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

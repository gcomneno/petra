#!/usr/bin/env python3
"""Multi-tier PET-METICA range sweep for bounded empirical comparison.

Runs `pet rewrite scan`-equivalent analysis at several (n_max, overscan) tiers,
optionally adds a high-overscan friction pass, and emits JSON plus a markdown
report with cross-tier stability notes.

All findings are bounded and descriptive — not theorems.
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
    family_report,
    graph_stats,
    one_step_return_costs,
    pick_asymmetries,
    pick_attractors,
    pick_surprises,
    scan_hubs,
    scan_pairs,
)

DEFAULT_SCAN_TIERS: tuple[tuple[int, int], ...] = (
    (30, 90),
    (50, 150),
    (75, 225),
    (100, 300),
)

DEFAULT_FRICTION_TIER: tuple[int, int] = (50, 50_000)


def _tier_label(n_max: int, overscan: int) -> str:
    return f"{n_max}-{overscan}"


def run_scan_tier(
    *,
    n_max: int,
    overscan: int,
    limit: int,
) -> dict[str, Any]:
    graph = build_graph(overscan=overscan)
    rows = scan_pairs(graph, n_max=n_max)
    hubs = scan_hubs(graph, n_max=n_max)
    return {
        "n_max": n_max,
        "overscan": overscan,
        "stats": graph_stats(graph, overscan=overscan),
        "top_hubs": hubs[:limit],
        "top_asymmetries": pick_asymmetries(rows, n_max=n_max, limit=limit),
        "top_attractors": pick_attractors(
            rows,
            n_max=n_max,
            limit=limit,
            min_incoming=5,
            min_outgoing=5,
        ),
        "surprises": pick_surprises(rows, limit=limit),
        "family_report": family_report(rows, n_max=n_max, primes=(2, 3, 5, 7)),
        "one_step_return_costs": one_step_return_costs(
            graph,
            n_max=n_max,
            limit=limit,
        ),
    }


def run_friction_tier(
    *,
    n_max: int,
    overscan: int,
    limit: int,
) -> dict[str, Any]:
    graph = build_graph(overscan=overscan)
    return {
        "n_max": n_max,
        "overscan": overscan,
        "stats": graph_stats(graph, overscan=overscan),
        "one_step_return_costs": one_step_return_costs(
            graph,
            n_max=n_max,
            limit=limit,
        ),
    }


def _hub_nodes(tier: dict[str, Any], *, count: int) -> list[int]:
    return [row["node"] for row in tier["top_hubs"][:count]]


def _prime_friction(tier: dict[str, Any]) -> list[dict[str, Any]]:
    return tier["one_step_return_costs"]["by_prime"]


def _friction_monotonic(by_prime: list[dict[str, Any]]) -> bool | None:
    avgs = [row["avg_back_cost"] for row in by_prime if row.get("count", 0) > 0]
    if len(avgs) < 2:
        return None
    return all(avgs[i] <= avgs[i + 1] for i in range(len(avgs) - 1))


def _family_tail_scores(
    tier: dict[str, Any],
    *,
    prime: int,
) -> list[dict[str, Any]]:
    key = f"p={prime}"
    return tier["family_report"].get(key, [])


def compare_tiers(
    tiers: list[dict[str, Any]],
    *,
    baseline_index: int = 0,
    hub_top: int = 5,
) -> dict[str, Any]:
    if not tiers:
        return {}

    baseline = tiers[baseline_index]
    baseline_hubs = set(_hub_nodes(baseline, count=hub_top))

    hub_persistence: list[dict[str, Any]] = []
    friction_checks: list[dict[str, Any]] = []
    dyadic_trends: list[dict[str, Any]] = []

    for tier in tiers:
        label = _tier_label(tier["n_max"], tier["overscan"])
        top10 = set(_hub_nodes(tier, count=10))
        overlap = sorted(baseline_hubs & top10)
        hub_persistence.append(
            {
                "tier": label,
                "baseline_top5_in_tier_top10": overlap,
                "overlap_count": len(overlap),
            }
        )

        by_prime = _prime_friction(tier)
        friction_checks.append(
            {
                "tier": label,
                "by_prime": by_prime,
                "avg_back_cost_monotonic_by_prime": _friction_monotonic(by_prime),
            }
        )

        fam = _family_tail_scores(tier, prime=2)
        if fam:
            last = fam[-1]
            dyadic_trends.append(
                {
                    "tier": label,
                    "largest_dyadic_node": last["node"],
                    "attractor_score": last["attractor_score"],
                }
            )

    return {
        "baseline_tier": _tier_label(baseline["n_max"], baseline["overscan"]),
        "hub_persistence_vs_baseline_top5": hub_persistence,
        "friction_by_tier": friction_checks,
        "dyadic_tail_attractor_scores": dyadic_trends,
    }


def build_payload(
    *,
    scan_tiers: list[tuple[int, int]],
    friction_tier: tuple[int, int] | None,
    limit: int,
) -> dict[str, Any]:
    tiers = [run_scan_tier(n_max=n, overscan=o, limit=limit) for n, o in scan_tiers]
    friction = None
    if friction_tier is not None:
        n_max, overscan = friction_tier
        friction = run_friction_tier(n_max=n_max, overscan=overscan, limit=limit)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_tiers": [{"n_max": n, "overscan": o} for n, o in scan_tiers],
        "friction_tier": (
            {"n_max": friction_tier[0], "overscan": friction_tier[1]}
            if friction_tier
            else None
        ),
        "limit": limit,
        "tiers": tiers,
        "friction_extended": friction,
        "comparison": compare_tiers(tiers),
    }


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# PET-METICA multi-range sweep",
        "",
        "This report compares bounded PET-METICA rewrite scans across several",
        " `(n_max, overscan)` tiers. Findings are descriptive and bounded.",
        "",
        "## Scope",
        "",
        f"- generated at (UTC): `{payload['generated_at']}`",
        f"- report limit: `{payload['limit']}`",
        f"- scan tiers: `{payload['scan_tiers']}`",
    ]

    if payload["friction_tier"]:
        ft = payload["friction_tier"]
        lines.append(
            f"- extended friction tier: `n_max={ft['n_max']}`, "
            f"`overscan={ft['overscan']}`"
        )

    lines.extend(
        [
            "- reproduction command:",
            "",
            "    tools/research/pet_metica_range_sweep.py \\",
            "      --output-json docs/reports/data/metica-range-sweep.json \\",
            "      --output-md docs/reports/generated/metica-range-sweep.md",
            "",
            "## Observations",
            "",
        ]
    )

    for tier in payload["tiers"]:
        label = _tier_label(tier["n_max"], tier["overscan"])
        stats = tier["stats"]
        lines.extend(
            [
                f"### Tier `{label}` (`1..{tier['n_max']}`, overscan `{tier['overscan']}`)",
                "",
                f"- active nodes: `{stats['active_node_count']}` / `{stats['node_count']}`",
                f"- edges: `{stats['edge_count']}`",
                f"- distinct rewrite labels: `{stats['distinct_label_count']}`",
                "",
                "Top hubs:",
                "",
                _md_table(
                    ["node", "hub_score"],
                    [[row["node"], row["hub_score"]] for row in tier["top_hubs"]],
                ),
                "",
                "Rewrite friction by prime:",
                "",
                _md_table(
                    ["prime", "count", "min", "max", "avg_back_cost"],
                    [
                        [
                            row["prime"],
                            row["count"],
                            row["min_back_cost"],
                            row["max_back_cost"],
                            row["avg_back_cost"],
                        ]
                        for row in tier["one_step_return_costs"]["by_prime"]
                    ],
                ),
                "",
                "Top asymmetries:",
                "",
                _md_table(
                    ["a", "b", "d_ab", "d_ba", "asymmetry"],
                    [
                        [
                            row["a"],
                            row["b"],
                            row["d_ab"],
                            row["d_ba"],
                            row["asymmetry"],
                        ]
                        for row in tier["top_asymmetries"][:5]
                    ],
                ),
                "",
            ]
        )

    comparison = payload["comparison"]
    lines.extend(["## Cross-tier comparison", ""])

    lines.extend(
        [
            "Baseline hub persistence (baseline top-5 appearing in each tier top-10):",
            "",
            _md_table(
                ["tier", "overlap_count", "shared_nodes"],
                [
                    [
                        row["tier"],
                        row["overlap_count"],
                        ", ".join(str(n) for n in row["baseline_top5_in_tier_top10"]),
                    ]
                    for row in comparison["hub_persistence_vs_baseline_top5"]
                ],
            ),
            "",
            "Friction monotonicity check (`avg_back_cost` non-decreasing by prime):",
            "",
            _md_table(
                ["tier", "monotonic"],
                [
                    [
                        row["tier"],
                        row["avg_back_cost_monotonic_by_prime"],
                    ]
                    for row in comparison["friction_by_tier"]
                ],
            ),
            "",
        ]
    )

    if payload["friction_extended"]:
        ext = payload["friction_extended"]
        label = _tier_label(ext["n_max"], ext["overscan"])
        lines.extend(
            [
                f"### Extended friction tier `{label}`",
                "",
                "High-overscan friction pass (for prime-level return costs only):",
                "",
                _md_table(
                    ["prime", "count", "min", "max", "avg_back_cost"],
                    [
                        [
                            row["prime"],
                            row["count"],
                            row["min_back_cost"],
                            row["max_back_cost"],
                            row["avg_back_cost"],
                        ]
                        for row in ext["one_step_return_costs"]["by_prime"]
                    ],
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation and limits",
            "",
            "1. Hub rankings and asymmetry tables are valid only within each tier's",
            "   explicit `(n_max, overscan)` window.",
            "2. Cross-tier overlap measures stability of earlier observations, not",
            "   proof of global structure.",
            "3. Prime-level friction ordering is an empirical pattern in bounded scans;",
            "   it is not a theorem about asymptotic rewrite geometry.",
            "4. Extended friction tiers use large overscan to approximate return paths;",
            "   they are computationally heavier and still bounded.",
            "",
            "## Non-claims",
            "",
            "This report does not claim:",
            "",
            "- global hub rankings beyond the stated tiers",
            "- asymptotic friction growth laws",
            "- completeness of PET-METICA geometry",
            "- invariance under all overscan choices",
            "",
        ]
    )

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run multi-tier PET-METICA range sweeps and emit comparison reports.",
    )
    parser.add_argument(
        "--tier",
        action="append",
        metavar="N_MAX:OVERSCAN",
        help="Scan tier as n_max:overscan (repeatable). Defaults to built-in ladder.",
    )
    parser.add_argument(
        "--friction-tier",
        metavar="N_MAX:OVERSCAN",
        help="Optional high-overscan friction-only tier (default: 50:50000).",
    )
    parser.add_argument(
        "--no-friction-tier",
        action="store_true",
        help="Skip the extended high-overscan friction pass.",
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON payload to stdout.",
    )
    return parser


def _parse_tier(text: str) -> tuple[int, int]:
    n_max_str, overscan_str = text.split(":", 1)
    return int(n_max_str), int(overscan_str)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.tier:
        scan_tiers = tuple(_parse_tier(t) for t in args.tier)
    else:
        scan_tiers = DEFAULT_SCAN_TIERS

    friction_tier: tuple[int, int] | None
    if args.no_friction_tier:
        friction_tier = None
    elif args.friction_tier:
        friction_tier = _parse_tier(args.friction_tier)
    else:
        friction_tier = DEFAULT_FRICTION_TIER

    payload = build_payload(
        scan_tiers=list(scan_tiers),
        friction_tier=friction_tier,
        limit=args.limit,
    )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(payload), encoding="utf-8")

    if args.json or (not args.output_json and not args.output_md):
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

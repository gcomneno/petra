import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet.atlas import extract_shape


def normalize_shape(node_list):
    shape = []

    for node in node_list:
        exp = node["e"]
        if exp is None:
            shape.append(("p", None))
        else:
            shape.append(("p", normalize_shape(exp)))

    return tuple(sorted(shape, key=str))


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a PET scan JSONL file for atlas-style reporting."
    )
    parser.add_argument("jsonl_path", help="Path to scan JSONL file")
    args = parser.parse_args()

    total = 0
    shapes = Counter()
    height_dist = Counter()
    branching_dist = Counter()

    max_node_count = (-1, None)
    max_height = (-1, None)
    max_branching = (-1, None)

    with open(args.jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            n = row["n"]
            metrics = row["metrics"]

            total += 1
            shapes[extract_shape(row["pet"])] += 1
            height_dist[metrics["height"]] += 1
            branching_dist[metrics["max_branching"]] += 1

            if metrics["node_count"] > max_node_count[0]:
                max_node_count = (metrics["node_count"], n)

            if metrics["height"] > max_height[0]:
                max_height = (metrics["height"], n)

            if metrics["max_branching"] > max_branching[0]:
                max_branching = (metrics["max_branching"], n)

    shape_entropy = 0.0
    if total:
        for count in shapes.values():
            p = count / total
            shape_entropy -= p * math.log(p)

    print(f"total_records: {total}")
    print(f"distinct_shapes: {len(shapes)}")
    print(f"shape_entropy: {shape_entropy:.12f}")
    print(f"max_entropy: {math.log(len(shapes)):.12f}" if shapes else "max_entropy: 0.000000000000")
    print(f"max_node_count: {max_node_count[0]}")
    print(f"first_n_with_max_node_count: {max_node_count[1]}")
    print(f"max_height: {max_height[0]}")
    print(f"first_n_with_max_height: {max_height[1]}")
    print(f"max_branching: {max_branching[0]}")
    print(f"first_n_with_max_branching: {max_branching[1]}")
    print()

    print("[height_distribution]")
    for h in sorted(height_dist):
        print(f"{h} {height_dist[h]}")

    print()
    print("[max_branching_distribution]")
    for b in sorted(branching_dist):
        print(f"{b} {branching_dist[b]}")


if __name__ == "__main__":
    main()

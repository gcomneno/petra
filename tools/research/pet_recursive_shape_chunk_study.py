#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

from pet.core import shape_signature_dict


@dataclass(frozen=True)
class ShapeInfo:
    value: int
    digits: int
    generator: int
    child_generators: tuple[int, ...]
    signature_size: int
    complexity: int


def shape_info(value: int) -> ShapeInfo:
    data = shape_signature_dict(value)
    child_generators = tuple(int(x) for x in data.get("child_generators", []))
    signature = data.get("signature", [])

    generator = int(data.get("generator"))
    signature_size = len(str(signature))

    complexity = (
        len(str(generator))
        + len(child_generators)
        + signature_size
    )

    return ShapeInfo(
        value=value,
        digits=len(str(value)),
        generator=generator,
        child_generators=child_generators,
        signature_size=signature_size,
        complexity=complexity,
    )


def parse_segment(segment: str) -> int | None:
    if not segment:
        return None
    value = int(segment)
    if value < 2:
        return None
    return value


def split_candidates(segment: str):
    for index in range(1, len(segment)):
        left_s = segment[:index]
        right_s = segment[index:]

        left = parse_segment(left_s)
        right = parse_segment(right_s)

        if left is None or right is None:
            continue

        yield index, left_s, right_s, left, right


def safe_pet_generator(value: int) -> int | None:
    if value < 2:
        return None
    return shape_info(value).generator


def merge_candidates(left: ShapeInfo, right: ShapeInfo) -> dict[str, tuple[int, int | None]]:
    product_value = left.generator * right.generator
    gcd_value = math.gcd(left.generator, right.generator)
    lcm_value = math.lcm(left.generator, right.generator)

    return {
        "left": (left.generator, left.generator),
        "right": (right.generator, right.generator),
        "product": (product_value, safe_pet_generator(product_value)),
        "gcd": (gcd_value, safe_pet_generator(gcd_value)),
        "lcm": (lcm_value, safe_pet_generator(lcm_value)),
    }


def best_merge_candidate(
    parent: ShapeInfo, left: ShapeInfo, right: ShapeInfo
) -> tuple[str, int, int | None, bool]:
    candidates = merge_candidates(left, right)

    def rank(item: tuple[str, tuple[int, int | None]]) -> tuple[int, int, int]:
        source, (value, generator) = item
        exact = 1 if generator == parent.generator else 0
        present_as_child = 1 if generator in (left.generator, right.generator) else 0
        non_null = 1 if generator is not None else 0
        size_penalty = -len(str(value))
        return exact, present_as_child, non_null + size_penalty

    source, (value, generator) = max(candidates.items(), key=rank)
    return source, value, generator, generator == parent.generator


def split_score(
    parent: ShapeInfo, left: ShapeInfo, right: ShapeInfo
) -> tuple[int, int, int, str, int, int | None, bool, dict[str, tuple[int, int | None]]]:
    child_complexity = max(left.complexity, right.complexity)
    condensation_gain = parent.complexity - child_complexity

    best_source, best_value, best_generator, best_matches_parent = best_merge_candidate(
        parent, left, right
    )
    merge_match_bonus = 5 if best_matches_parent else 0

    generator_match_bonus = 0
    if parent.generator in (left.generator, right.generator):
        generator_match_bonus += 3
    if left.generator == right.generator:
        generator_match_bonus += 1

    generator_diversity = len({left.generator, right.generator})

    return (
        condensation_gain,
        generator_match_bonus,
        generator_diversity,
        best_source,
        best_value,
        best_generator,
        best_matches_parent,
        merge_candidates(left, right),
    )



def classify_failure_mode(
    parent: ShapeInfo,
    left: ShapeInfo,
    right: ShapeInfo,
    lcm_generator: int | None,
    condensation_gain: int,
    parent_seen_in_child: bool,
    lcm_matches_parent: bool,
) -> str:
    if parent_seen_in_child or lcm_matches_parent:
        return "local-preservation-success"

    local_generators = [
        left.generator,
        right.generator,
    ]

    if lcm_generator is not None:
        local_generators.append(lcm_generator)

    local_max = max(local_generators)

    if parent.generator > local_max:
        return "emergent-global-generator"

    if condensation_gain > 0:
        return "split-overcompression"

    return "no-local-support"


def classify_split(
    condensation_gain: int,
    generator_match_bonus: int,
    parent: ShapeInfo,
    left: ShapeInfo,
    right: ShapeInfo,
    lcm_generator: int | None,
) -> str:
    parent_seen_in_child = parent.generator in (left.generator, right.generator)
    lcm_matches_parent = lcm_generator == parent.generator

    if lcm_matches_parent and not parent_seen_in_child:
        return "parent-reconstructed-by-lcm"
    if lcm_matches_parent and parent_seen_in_child:
        return "parent-preserved-and-lcm-stable"
    if parent_seen_in_child:
        return "parent-preserved-locally"
    if condensation_gain > 0 and generator_match_bonus > 0:
        return "strong-condensing-split"
    if condensation_gain > 0:
        return "condensing-split"
    if generator_match_bonus > 0:
        return "shape-related-split"
    return "weak-or-noisy-split"


def best_split(segment: str):
    parent_value = parse_segment(segment)
    if parent_value is None:
        return None

    parent = shape_info(parent_value)
    best = None

    for index, left_s, right_s, left_value, right_value in split_candidates(segment):
        left = shape_info(left_value)
        right = shape_info(right_value)

        (
            condensation_gain,
            generator_match_bonus,
            generator_diversity,
            best_merge_source,
            best_merge_value,
            best_merge_generator,
            best_merge_matches_parent,
            all_merge_candidates,
        ) = split_score(parent, left, right)

        merge_match_bonus = 5 if best_merge_matches_parent else 0

        ranking = (
            merge_match_bonus,
            generator_match_bonus,
            condensation_gain,
            -generator_diversity,
            -abs(len(left_s) - len(right_s)),
        )

        row = {
            "index": index,
            "left_s": left_s,
            "right_s": right_s,
            "parent": parent,
            "left": left,
            "right": right,
            "condensation_gain": condensation_gain,
            "generator_match_bonus": generator_match_bonus,
            "generator_diversity": generator_diversity,
            "product_value": all_merge_candidates["product"][0],
            "product_generator": all_merge_candidates["product"][1],
            "gcd_value": all_merge_candidates["gcd"][0],
            "gcd_generator": all_merge_candidates["gcd"][1],
            "lcm_value": all_merge_candidates["lcm"][0],
            "lcm_generator": all_merge_candidates["lcm"][1],
            "best_merge_source": best_merge_source,
            "best_merge_value": best_merge_value,
            "best_merge_generator": best_merge_generator,
            "best_merge_matches_parent": best_merge_matches_parent,
            "parent_seen_in_child": parent.generator in (left.generator, right.generator),
            "lcm_matches_parent": all_merge_candidates["lcm"][1] == parent.generator,
            "failure_mode": classify_failure_mode(
                parent,
                left,
                right,
                all_merge_candidates["lcm"][1],
                condensation_gain,
                parent.generator in (left.generator, right.generator),
                all_merge_candidates["lcm"][1] == parent.generator,
            ),
            "split_status": classify_split(
                condensation_gain,
                generator_match_bonus,
                parent,
                left,
                right,
                all_merge_candidates["lcm"][1],
            ),
            "ranking": ranking,
        }

        if best is None or ranking > best["ranking"]:
            best = row

    return best


def walk(root: str, max_depth: int):
    rows = []

    def visit(segment: str, depth: int, path: str):
        parent_value = parse_segment(segment)
        if parent_value is None:
            return

        parent = shape_info(parent_value)

        if depth >= max_depth or len(segment) <= 1:
            rows.append({
                "path": path,
                "depth": depth,
                "segment": segment,
                "parent": parent,
                "split": "-",
                "left": "-",
                "right": "-",
                "left_generator": "-",
                "right_generator": "-",
                "condensation_gain": "-",
                "generator_match_bonus": "-",
                "product_value": "-",
                "product_generator": "-",
                "gcd_value": "-",
                "gcd_generator": "-",
                "lcm_value": "-",
                "lcm_generator": "-",
                "best_merge_source": "-",
                "best_merge_value": "-",
                "best_merge_generator": "-",
                "best_merge_matches_parent": "-",
                "parent_seen_in_child": "-",
                "lcm_matches_parent": "-",
                "failure_mode": "-",
                "split_status": "atomic",
            })
            return

        split = best_split(segment)
        if split is None:
            rows.append({
                "path": path,
                "depth": depth,
                "segment": segment,
                "parent": parent,
                "split": "-",
                "left": "-",
                "right": "-",
                "left_generator": "-",
                "right_generator": "-",
                "condensation_gain": "-",
                "generator_match_bonus": "-",
                "product_value": "-",
                "product_generator": "-",
                "gcd_value": "-",
                "gcd_generator": "-",
                "lcm_value": "-",
                "lcm_generator": "-",
                "best_merge_source": "-",
                "best_merge_value": "-",
                "best_merge_generator": "-",
                "best_merge_matches_parent": "-",
                "parent_seen_in_child": "-",
                "lcm_matches_parent": "-",
                "failure_mode": "-",
                "split_status": "no-split",
            })
            return

        rows.append({
            "path": path,
            "depth": depth,
            "segment": segment,
            "parent": parent,
            "split": split["index"],
            "left": split["left_s"],
            "right": split["right_s"],
            "left_generator": split["left"].generator,
            "right_generator": split["right"].generator,
            "condensation_gain": split["condensation_gain"],
            "generator_match_bonus": split["generator_match_bonus"],
            "product_value": split["product_value"],
            "product_generator": split["product_generator"],
            "gcd_value": split["gcd_value"],
            "gcd_generator": split["gcd_generator"],
            "lcm_value": split["lcm_value"],
            "lcm_generator": split["lcm_generator"],
            "best_merge_source": split["best_merge_source"],
            "best_merge_value": split["best_merge_value"],
            "best_merge_generator": split["best_merge_generator"],
            "best_merge_matches_parent": split["best_merge_matches_parent"],
            "parent_seen_in_child": split["parent_seen_in_child"],
            "lcm_matches_parent": split["lcm_matches_parent"],
            "failure_mode": split["failure_mode"],
            "split_status": split["split_status"],
        })

        if split["split_status"] in {
            "strong-condensing-split",
            "condensing-split",
            "shape-related-split",
        }:
            visit(split["left_s"], depth + 1, path + "L")
            visit(split["right_s"], depth + 1, path + "R")

    visit(root, 0, "root")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="+")
    parser.add_argument("--max-depth", type=int, default=2)
    args = parser.parse_args()

    print(
        "N\tpath\tdepth\tsegment\tsegment_digits\tsegment_generator\t"
        "segment_complexity\tsplit\tleft\tright\tleft_generator\t"
        "right_generator\tcondensation_gain\tgenerator_match_bonus\t"
        "product_value\tproduct_generator\tgcd_value\tgcd_generator\t"
        "lcm_value\tlcm_generator\tbest_merge_source\tbest_merge_value\t"
        "best_merge_generator\tbest_merge_matches_parent\t"
        "parent_seen_in_child\tlcm_matches_parent\t"
        "failure_mode\tsplit_status"
    )

    for raw in args.numbers:
        for row in walk(raw, args.max_depth):
            parent = row["parent"]
            print(
                f"{raw}\t"
                f"{row['path']}\t"
                f"{row['depth']}\t"
                f"{row['segment']}\t"
                f"{parent.digits}\t"
                f"{parent.generator}\t"
                f"{parent.complexity}\t"
                f"{row['split']}\t"
                f"{row['left']}\t"
                f"{row['right']}\t"
                f"{row['left_generator']}\t"
                f"{row['right_generator']}\t"
                f"{row['condensation_gain']}\t"
                f"{row['generator_match_bonus']}\t"
                f"{row['product_value']}\t"
                f"{row['product_generator']}\t"
                f"{row['gcd_value']}\t"
                f"{row['gcd_generator']}\t"
                f"{row['lcm_value']}\t"
                f"{row['lcm_generator']}\t"
                f"{row['best_merge_source']}\t"
                f"{row['best_merge_value']}\t"
                f"{row['best_merge_generator']}\t"
                f"{row['best_merge_matches_parent']}\t"
                f"{row['parent_seen_in_child']}\t"
                f"{row['lcm_matches_parent']}\t"
                f"{row['failure_mode']}\t"
                f"{row['split_status']}"
            )


if __name__ == "__main__":
    main()

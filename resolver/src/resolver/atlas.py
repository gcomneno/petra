"""Shape atlas for PETRA canonical shapes.

A shape atlas maps integers to their canonical PETRA shapes and groups
them by structural identity. The atlas is a derived layer on top of the
Resolver: it uses ``int_to_shape`` for construction and the canonical
serialization as the grouping key.

The atlas is static: PETRA shapes are canonical and deterministic, so a
given integer always has the same shape. Once the atlas is built, all
queries are O(1).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from petra import serialize_shape

from .distance import int_to_shape


@dataclass(frozen=True)
class ShapeAtlas:
    """A finite map from integers to canonical PETRA shapes."""

    by_shape: dict[str, tuple[int, ...]]
    by_number: dict[int, str]

    @property
    def shape_count(self) -> int:
        return len(self.by_shape)

    @property
    def number_count(self) -> int:
        return len(self.by_number)

    def shape_of(self, n: int) -> str:
        try:
            return self.by_number[n]
        except KeyError as error:
            raise KeyError(f"number {n} not in atlas") from error

    def numbers_with_shape(self, shape: str) -> tuple[int, ...]:
        try:
            return self.by_shape[shape]
        except KeyError as error:
            raise KeyError(f"shape {shape} not in atlas") from error


def build_shape_atlas(
    low: int,
    high: int,
    *,
    progress: bool = False,
) -> ShapeAtlas:
    """Build a shape atlas over the closed range [low, high]."""

    if low < 1:
        raise ValueError("low must be >= 1")
    if high < low:
        raise ValueError("high must be >= low")

    by_shape: dict[str, list[int]] = {}
    by_number: dict[int, str] = {}

    for n in range(low, high + 1):
        if progress and (n - low) % 10_000 == 0 and n > low:
            done = n - low
            total = high - low + 1
            print(f"  {done}/{total}...")
        try:
            shape = int_to_shape(n)
        except Exception:
            continue
        text = serialize_shape(shape)
        by_shape.setdefault(text, []).append(n)
        by_number[n] = text

    return ShapeAtlas(
        by_shape={k: tuple(v) for k, v in by_shape.items()},
        by_number=by_number,
    )


def save_shape_atlas(atlas: ShapeAtlas, path: str | Path) -> None:
    """Save a shape atlas to a JSON file."""

    payload = {
        "schema": "resolver.shape-atlas.v1",
        "shape_count": atlas.shape_count,
        "number_count": atlas.number_count,
        "by_shape": {
            shape: list(numbers)
            for shape, numbers in atlas.by_shape.items()
        },
    }
    with open(path, "w") as f:
        json.dump(payload, f, sort_keys=True, separators=(",", ":"))


def load_shape_atlas(path: str | Path) -> ShapeAtlas:
    """Load a shape atlas from a JSON file."""

    with open(path) as f:
        payload = json.load(f)

    by_shape = {
        shape: tuple(numbers)
        for shape, numbers in payload["by_shape"].items()
    }
    by_number: dict[int, str] = {}
    for shape, numbers in by_shape.items():
        for n in numbers:
            by_number[n] = shape

    return ShapeAtlas(by_shape=by_shape, by_number=by_number)


def iter_shapes_by_size(
    atlas: ShapeAtlas,
) -> Iterator[tuple[str, tuple[int, ...]]]:
    """Yield (shape, numbers) sorted by decreasing cluster size."""

    yield from sorted(
        atlas.by_shape.items(),
        key=lambda item: -len(item[1]),
    )

@dataclass(frozen=True)
class DistanceAtlas:
    """A finite map from pairs of canonical shapes to edit distances."""

    by_pair: dict[tuple[str, str], int]

    @property
    def pair_count(self) -> int:
        return len(self.by_pair)

    def distance(self, shape_a: str, shape_b: str) -> int:
        if shape_a == shape_b:
            return 0
        key = (
            (shape_a, shape_b)
            if shape_a <= shape_b
            else (shape_b, shape_a)
        )
        try:
            return self.by_pair[key]
        except KeyError as error:
            raise KeyError(
                f"pair ({shape_a}, {shape_b}) not in atlas"
            ) from error


def build_distance_atlas(
    shape_atlas: ShapeAtlas,
    *,
    max_depth: int = 30,
    max_nodes: int = 80,
    max_visited: int = 200_000,
    progress_every: int = 500,
) -> DistanceAtlas:
    """Compute pairwise structural distances between all distinct shapes."""

    from .distance import DistanceCache, int_to_shape
    from petra import parse_shape

    shapes: dict[str, object] = {}
    for text in shape_atlas.by_shape:
        shapes[text] = parse_shape(text)

    shape_texts = sorted(shapes.keys())
    n = len(shape_texts)
    total_pairs = n * (n - 1) // 2

    print(
        f"Distance atlas: {n} shapes, {total_pairs} pairs, "
        f"max_nodes={max_nodes}"
    )

    cache = DistanceCache(
        max_depth=max_depth,
        max_nodes=max_nodes,
        max_visited=max_visited,
    )
    by_pair: dict[tuple[str, str], int] = {}

    done = 0
    for i, text_a in enumerate(shape_texts):
        for j in range(i + 1, n):
            text_b = shape_texts[j]
            distance = cache.distance(shapes[text_a], shapes[text_b])
            key = (
                (text_a, text_b)
                if text_a <= text_b
                else (text_b, text_a)
            )
            by_pair[key] = distance
            done += 1
            if progress_every and done % progress_every == 0:
                print(f"  {done}/{total_pairs}...")

    return DistanceAtlas(by_pair=by_pair)


def save_distance_atlas(
    atlas: DistanceAtlas,
    path: str | Path,
) -> None:
    """Save a distance atlas to a JSON file."""

    payload = {
        "schema": "resolver.distance-atlas.v1",
        "pair_count": atlas.pair_count,
        "by_pair": [
            {
                "a": key[0],
                "b": key[1],
                "distance": distance,
            }
            for key, distance in atlas.by_pair.items()
        ],
    }
    with open(path, "w") as f:
        json.dump(payload, f, sort_keys=True, separators=(",", ":"))


def load_distance_atlas(path: str | Path) -> DistanceAtlas:
    """Load a distance atlas from a JSON file."""

    with open(path) as f:
        payload = json.load(f)

    by_pair = {
        (entry["a"], entry["b"]): entry["distance"]
        for entry in payload["by_pair"]
    }

    return DistanceAtlas(by_pair=by_pair)

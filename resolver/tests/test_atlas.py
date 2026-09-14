"""Tests for the Resolver atlas layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from petra import parse_shape, serialize_shape
from resolver import (
    AtlasBackedDistance,
    DistanceAtlas,
    ShapeAtlas,
    build_shape_atlas,
    iter_shapes_by_size,
    load_distance_atlas,
    load_shape_atlas,
    save_distance_atlas,
    save_shape_atlas,
)


# ---------------------------------------------------------------------------
# ShapeAtlas
# ---------------------------------------------------------------------------


def test_build_shape_atlas_small_range() -> None:
    atlas = build_shape_atlas(2, 30)
    assert atlas.number_count == 29
    assert atlas.shape_count >= 5  # several distinct shapes in this range
    assert "C(r0^1)" in atlas.by_shape  # includes the prime shape


def test_shape_atlas_shape_of() -> None:
    atlas = build_shape_atlas(2, 30)
    assert atlas.shape_of(6) == "C(r0^1,r1^1)"
    assert atlas.shape_of(10) == "C(r0^1,r1^1)"
    assert atlas.shape_of(12) == "C(r0^C(r0^1),r1^1)"


def test_shape_atlas_shape_of_missing_number() -> None:
    atlas = build_shape_atlas(2, 30)
    with pytest.raises(KeyError):
        atlas.shape_of(999)


def test_shape_atlas_numbers_with_shape() -> None:
    atlas = build_shape_atlas(2, 30)
    semiprimes = atlas.numbers_with_shape("C(r0^1,r1^1)")
    assert 6 in semiprimes
    assert 10 in semiprimes
    assert 15 in semiprimes


def test_shape_atlas_numbers_with_unknown_shape() -> None:
    atlas = build_shape_atlas(2, 30)
    with pytest.raises(KeyError):
        atlas.numbers_with_shape("C(r99^1)")


def test_shape_atlas_save_load_roundtrip(tmp_path: Path) -> None:
    atlas = build_shape_atlas(2, 30)
    path = tmp_path / "atlas.json"
    save_shape_atlas(atlas, path)
    loaded = load_shape_atlas(path)
    assert loaded.shape_count == atlas.shape_count
    assert loaded.number_count == atlas.number_count
    assert loaded.by_shape == atlas.by_shape


def test_iter_shapes_by_size_orders_descending() -> None:
    atlas = build_shape_atlas(2, 30)
    sizes = [len(numbers) for _, numbers in iter_shapes_by_size(atlas)]
    assert sizes == sorted(sizes, reverse=True)


def test_build_shape_atlas_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        build_shape_atlas(0, 10)
    with pytest.raises(ValueError):
        build_shape_atlas(10, 5)


# ---------------------------------------------------------------------------
# DistanceAtlas
# ---------------------------------------------------------------------------


def _small_distance_atlas() -> DistanceAtlas:
    """In-memory distance atlas with a few known pairs, no computation."""

    a = "C(r0^1)"
    b = "C(r0^1,r1^1)"
    c = "C(r0^C(r0^1))"
    d = "C(r0^C(r0^1),r1^1)"

    return DistanceAtlas(
        by_pair={
            (a, b): 1,
            (a, c): 1,
            (a, d): 2,
            (b, c): 2,
            (b, d): 1,
            (c, d): 1,
        }
    )


def test_distance_atlas_identity_is_zero() -> None:
    atlas = _small_distance_atlas()
    a = "C(r0^1)"
    assert atlas.distance(a, a) == 0


def test_distance_atlas_returns_stored_value() -> None:
    atlas = _small_distance_atlas()
    assert atlas.distance("C(r0^1)", "C(r0^1,r1^1)") == 1


def test_distance_atlas_is_symmetric_on_lookup() -> None:
    atlas = _small_distance_atlas()
    a = "C(r0^1)"
    b = "C(r0^1,r1^1)"
    assert atlas.distance(a, b) == atlas.distance(b, a)


def test_distance_atlas_missing_pair_raises() -> None:
    atlas = _small_distance_atlas()
    with pytest.raises(KeyError):
        atlas.distance("C(r0^1)", "C(r0^1,r1^1,r2^1,r3^1)")


def test_distance_atlas_save_load_roundtrip(tmp_path: Path) -> None:
    atlas = _small_distance_atlas()
    path = tmp_path / "distances.json"
    save_distance_atlas(atlas, path)
    loaded = load_distance_atlas(path)
    assert loaded.by_pair == atlas.by_pair


# ---------------------------------------------------------------------------
# AtlasBackedDistance
# ---------------------------------------------------------------------------


def test_atlas_backed_uses_atlas_for_known_pair() -> None:
    oracle = AtlasBackedDistance(_small_distance_atlas())
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    assert oracle.distance_shapes(a, b) == 1
    assert oracle.atlas_hits == 1
    assert oracle.runtime_misses == 0


def test_atlas_backed_identity_does_not_increment_counters() -> None:
    oracle = AtlasBackedDistance(_small_distance_atlas())
    a = parse_shape("C(r0^1)")
    assert oracle.distance_shapes(a, a) == 0
    assert oracle.atlas_hits == 0
    assert oracle.runtime_misses == 0


def test_atlas_backed_falls_back_to_resolver() -> None:
    oracle = AtlasBackedDistance(_small_distance_atlas())
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1,r2^1,r3^1)")
    # Pair not in the small atlas: fallback to the Resolver.
    assert oracle.distance_shapes(a, b) == 3
    assert oracle.atlas_hits == 0
    assert oracle.runtime_misses == 1


def test_atlas_backed_distance_numbers() -> None:
    oracle = AtlasBackedDistance(_small_distance_atlas())
    assert oracle.distance_numbers(6, 12) == 1
    assert oracle.distance_numbers(6, 10) == 0


def test_atlas_backed_from_path(tmp_path: Path) -> None:
    path = tmp_path / "distances.json"
    save_distance_atlas(_small_distance_atlas(), path)
    oracle = AtlasBackedDistance.from_path(path)
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    assert oracle.distance_shapes(a, b) == 1
    assert oracle.atlas_pair_count == 6

# Resolver data artifacts

This directory contains precomputed atlases produced by the Resolver
over bounded integer ranges.

## Files

- `shape-atlas-2-100000.json` — shape atlas over the closed range
  `[2, 100000]`. Maps each integer in the range to its canonical PETRA
  shape, and groups integers by structural identity.

- `distance-atlas-2-100000.json` — distance atlas over the shape atlas
  above. Maps each unordered pair of distinct shapes to its structural
  edit distance, computed with `max_nodes=80`.

- `distance-atlas-2-100000-report.txt` — human-readable analysis of the
  distance atlas: distribution of distances, most distant shape pairs,
  most isolated shapes, most central shapes.

## Properties

- shape count: 123 distinct shapes
- number count: 99999 integers
- pair count: 7503 shape pairs
- distance range: 1 to 8 edits
- distance mean: approximately 3.6

## Regeneration

From the repository root, with the Resolver installed, run the Python
snippet shown in the source file `resolver/src/resolver/atlas.py` under
`build_shape_atlas` and `build_distance_atlas`. In short:

    from resolver import (
        build_shape_atlas,
        build_distance_atlas,
        save_shape_atlas,
        save_distance_atlas,
    )
    shape_atlas = build_shape_atlas(2, 100_000)
    save_shape_atlas(shape_atlas, "resolver/data/shape-atlas-2-100000.json")
    distance_atlas = build_distance_atlas(shape_atlas, max_nodes=80)
    save_distance_atlas(distance_atlas, "resolver/data/distance-atlas-2-100000.json")

The distance atlas computation takes roughly 35 minutes on an older
machine and roughly 2 minutes on a modern one. The shape atlas alone
takes a few seconds.

## Observations from the report

Three structurally extreme shapes dominate the periphery of the shape
space:

- C(r0^C(r0^C(r0^C(r0^1)))) — the deepest tower in the range
- C(r0^1,r1^1,r2^1,r3^1,r4^1,r5^1) — the widest primorial in the range
- C(r0^1) — the atomic prime shape

Their average distances to the rest of the shape space are all around
5, and they are mutually distant. The "center" of the shape space is
populated by mixed shapes with 2 to 4 terms and moderate depth, whose
average distance to the rest is below 3.2.

## Boundary

These artifacts are research data. They do not extend PETRA semantics
and do not influence operator behavior. They are derived from
`resolver.int_to_shape` and the structural distance defined by the
Resolver.

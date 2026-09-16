# Flakiness of test_resolver: id() cache bug (T17)

Status: research note (bug fix)
Scope: intermittent failure of `test_wide_path_length_matches_width[8]`
Stability: root cause identified, fixed, verified
Thread: T17

## Symptom

`test_wide_path_length_matches_width[8]` failed intermittently when the
full suite was run, but always passed when run alone. On failure, the
path length was 10 instead of 8.

Reproduction rate in the full suite: ~2 in 10.

## Root cause

`_build_cached_metrics` in `resolver/src/resolver/search.py` cached
per-shape metrics in `dict[int, int]` keyed by `id(shape)`:

    key = id(shape)

`id()` is unique only among live objects. During A* search, shapes
that do not improve the frontier are discarded. The garbage collector
can free them and reuse their `id` for a new shape. The cache then
returns the old shape's metric, the heuristic is wrong, and A* returns
a suboptimal path.

This is heap-state dependent, which is why it fails only when the
suite is run (previous tests leave a heap that triggers reuse) and
never in isolation.

## Fix

Replaced `key = id(shape)` with `key = shape` in all four caches
(`node_cache`, `depth_cache`, `leaf_cache`, `heuristic_cache`). Shapes
are hashable by value, so the cache is now keyed by the shape itself
and cannot be confused by `id` reuse.

The docstring of `search.py` already claimed identity was never reused
within a call. The claim was wrong, and the fix removes the dependency
on it.

## Verification

- Before fix: 200 isolated runs of `resolve("1", wide_shape(8), ...)`
  gave lengths `{8, 10}`.
- After fix: 500 isolated runs give `{8}`.
- After fix: full suite `pytest tests/ resolver/tests/ -q` passes
  718/718, 3 skipped, for 10 consecutive runs.

## Cost

The cache now hashes the shape (recursive hash) instead of an integer.
For the tested suite, runtime is unchanged (~2.6 s).

## Status

T17 closed. Bug fixed.

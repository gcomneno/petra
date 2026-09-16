# Ruff and mypy clean on resolver (T18)

Status: research note (hygiene)
Scope: lint and type-check the resolver satellite
Stability: fixed
Thread: T18

## Context

T18 observed that adding `resolver/` to the CI's ruff and mypy checks
surfaced ~50 ruff errors and ~16 mypy errors. This note records the
fix.

## Ruff

- 50 errors found, 24 fixable automatically.
- Applied `ruff check . --fix` (28 fixed including the safe set).
- 26 remaining split into:
  - 16 false positives on `RUF001`/`RUF002` for the `×` (MULTIPLICATION
    SIGN), which is the PETRA container separator. Added to
    `resolver/pyproject.toml` ignore list.
  - 10 real issues: `SIM108` (ternary), `SIM110` (all), `RUF005`
    (unpacking), `RUF059` (unused unpack), `B905` (`zip` strict). All
    fixed with `--fix --unsafe-fixes`.
- Ruff clean on resolver.

## Mypy

- 18 errors found across 12 files.
- 10 were `petra` missing `py.typed`. Added `src/petra/py.typed`.
- 8 were real:
  - `search.py`: caches declared `dict[int, int]` but keyed by
    `PetraShape` since the T17 fix. Corrected to `dict[PetraShape, int]`.
  - `struct_destruct.py`: annotation for `replace_positions`, and
    `results` shadowing in the leaf branch (renamed to `leaf_results`).
  - `atlas.py`: `shapes` typed as `dict[str, object]`, corrected to
    `dict[str, PetraShape]`, with the import added.
- Mypy clean on resolver (13 source files).

## Verification

- `ruff check resolver/`: all checks passed.
- `cd resolver && mypy src/`: no issues in 13 source files.
- `pytest tests/ resolver/tests/ -q`: 718 passed, 3 skipped.

## Notes

A first pass placed the `RUF001`/`RUF002` ignore in the root
`pyproject.toml` instead of `resolver/pyproject.toml`. Reverted in
commit `7bfb94e`.

## Status

T18 closed. Ruff and mypy clean on resolver.

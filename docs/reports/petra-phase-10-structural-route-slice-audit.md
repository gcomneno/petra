# PETRA Phase 10 — Structural Route Slice Audit
<!-- docs-check: allow-stale-src-refs -->

## Context

Phase: 10 — fourth controlled historical runtime deletion.

Verdict: `READY_FOR_STRUCTURAL_ROUTE_SLICE`

Decision: `GO: DELETE STRUCTURAL_ROUTE`

The sole normative PETRA semantic authority remains
`docs/reference/SPEC.md`.

This audit records the removal of the historical structural route
subsystem: its runtime module, its CLI surface, its tool, and its test
coverage.

## Rationale

`pet.structural_route` implements a bounded first-match search over the
historical PET operator graph (NEW/DROP/INC/DEC). Its own module-level
claim states:

> selected path is first match in deterministic bounded traversal,
> not a global optimality claim

The Resolver (satellite project at `resolver/`) implements the same
concept on the maintained PETRA operators (SPROUT/SHED/GRAFT/PRUNE),
with A* search and a guaranteed minimal path.

The structural route subsystem is therefore not only historical: it is
conceptually superseded. Keeping it means maintaining two
implementations of the same idea, where the older one has weaker
guarantees and fewer tests.

## Selected deletion surface

### Runtime (1 file)

- `src/pet/structural_route.py` — 90 lines

Depends on:

- `pet.graph` (stays)
- `pet.object_model` (stays)
- `pet.traces` (stays)

None of those dependencies is removed by this slice.

### Tool (1 file)

- `tools/research/pet_structural_route_probe.py`

### Tests (2 files)

- `tests/test_cli_structural_route.py` — 3 tests, currently under the
  canonical gate (not matched by any legacy marker pattern; invokes the
  CLI via subprocess)
- `tests/test_tools_pet_structural_route_probe.py` — 4 tests, already
  under the legacy gate

### CLI surface (4 removal points in `src/pet/cli.py`)

1. Line 27: `from .structural_route import build_structural_route_result`
2. Lines 268–322: `_run_structural_route` (approximately 55 lines)
3. Lines 6062–6071: the `structural-route` subparser
4. Lines 7068–7069: the `structural-route` dispatch branch

## Documentation surface

Only historical and audit documents reference `pet.structural_route`:

- `docs/foundations/pet-module-stability-classification.md`
- `docs/foundations/pet-first-principles-implementation-audit.md`
- `docs/reports/petra-phase-10-legacy-runtime-dependency-audit.md`
- `docs/reports/petra-phase-10-second-legacy-deletion-audit.md`
- `docs/reports/petra-phase-10-scan-query-slice-audit.md`

These are evidence and audit documents, not active surfaces. They remain
on disk unmodified. The scan/query audit will be factually outdated on
one line after this slice (it lists `structural_route` as still
present), but rewriting a prior audit to reflect a later state is
contrary to the audit-as-snapshot principle. The next audit supersedes
it.

## Runtime dependency graph (post-slice)

After removal, `src/pet/` contains 15 Python files.

The `structural_route` edges disappear from the graph:

- ~~`pet.structural_route` → `graph`, `object_model`, `traces`~~
- ~~`pet.graph` inbound from `structural_route`~~

Remaining edges are unaffected.

## No `__init__.py` change

`pet.structural_route` is not exported by `pet/__init__.py`. No public
API symbol is removed by this slice.

## Verification plan

The slice is accepted only when:

1. no Python file outside `src/pet/` imports `pet.structural_route`;
2. `python3 -c "import pet.cli"` succeeds;
3. the canonical gate passes:
   `pytest -q -m "not slow and not legacy"`;
4. `docs-check` passes;
5. `git diff --check` is clean;
6. `src/petra` still has no dependency on `pet`.

Expected canonical test count after removal:

- before: 716 passed, 1 skipped
- after:  713 passed, 1 skipped (3 removed by
  `tests/test_cli_structural_route.py`)

The legacy gate loses 4 tests but is not part of the acceptance
criterion.

## What this slice does not remove

- `pet.graph`, `pet.object_model`, `pet.traces`: they have other
  consumers and stay.
- The tool `tools/research/atlas_summary.py`: unaffected.
- The historical audits: retained as evidence.

## Non-claims

This work does not claim that:

- the historical PET runtime is fully deleted;
- the remaining runtime modules are independently safe to delete;
- PETRA semantics have changed;
- the Resolver is a replacement for PETRA's canonical core;
- any historical audit is regenerated to reflect post-slice state.

The result establishes the fourth repetition of the Phase 10 pattern:

current dependency audit → freeze one inseparable historical cluster →
remove only that cluster → full regression → repeat.

# PETRA Phase 10 — Completion Audit

## Context

Phase: 10 — complete replacement of the historical PET runtime.

Verdict: `PHASE_10_COMPLETE`

Decision: `GO: HISTORICAL PET RUNTIME REMOVED`

The sole normative PETRA semantic authority remains
`docs/reference/SPEC.md`.

This audit closes Phase 10. It records the final removal of the
historical PET runtime and its coupled tooling, tests, and CLI surface.

## Chronology of Phase 10 slices

Phase 10 proceeded in controlled slices:

1. `pet.lens_api` — first leaf deletion.
2. `pet.rewrite_metric` cluster — second slice.
3. `pet.scan` + `pet.query` subsystem — third slice.
4. `pet.structural_route` — fourth slice.
5. **Full runtime removal** — this slice.

Slices 1–4 are recorded in their own audit documents under
`docs/reports/petra-phase-10-*.md`.

## What this final slice removes

### Runtime (`src/pet/`)

All 15 remaining modules:

`__init__.py`, `algebra.py`, `atlas.py`, `cli.py`, `core.py`,
`families.py`, `graph.py`, `guarded_redirect.py`, `io.py`, `metrics.py`,
`object_metrics.py`, `object_model.py`, `operators.py`, `root_base.py`,
`traces.py`.

### Tools

All `pet_*` scripts and the coupled triage/classic/legacy/research
tooling, including compatibility wrappers.

### Tests

90 test files across the legacy namespace, the CLI subprocess tests,
and the direct-import tests of `pet` modules.

### Configuration

- `pyproject.toml`: removed the `legacy` marker.
- `.github/workflows/ci.yml`: removed the legacy-only CI job.
- `tests/conftest.py`: reduced to marker registration.
- `tools/README.md`: rewritten for the post-Phase-10 tool surface.
- `docs/foundations/*` and `docs/research/notes/PET-METICA.md`: marked
  with `<!-- docs-check: allow-stale-src-refs -->` so historical
  citations of removed sources do not fail the documentation gate.

## What remains

- `src/petra/` — the canonical runtime, untouched.
- `resolver/` — the satellite project, untouched.
- `tests/test_petra_*.py` — 11 canonical test modules.
- `tests/test_report_contracts.py` — historical report contracts.
- `tests/test_make_demo.py` — PETRA demo smoke test.
- `tests/conftest.py` — minimal.
- `tools/research/*.py` — a small set of shape analysis helpers that
  do not depend on `pet`.
- `docs/` — the specification, vision, roadmap, status, historical
  audits, and research notes.

## Gate impact

- canonical test gate (pytest): 539 passed, 3 skipped.
- docs gate: passes.
- ruff: unchanged; `src/petra/` still the only lint target.
- mypy: unchanged.

## Dependency verification

- `src/petra` has no dependency on `pet` (verified).
- the Resolver has no dependency on `pet` (verified).
- the remaining `tools/research/*.py` scripts do not import `pet`.

## Replacement policy

Historical PET behavior remains recoverable through Git history. The
tag `v0.3.0` preserves the final historical PET release.

The removal is not a compatibility break for PETRA: PETRA never
depended on PET.

## Non-claims

This work does not claim that:

- the historical PET runtime can be restored without Git history;
- any historical report is regenerable from the working tree;
- all research material under `docs/research/` is now active;
- the Resolver is a replacement for PETRA's core.

The result closes Phase 10. The repository now contains exactly two
Python distributions: the canonical PETRA runtime and the Resolver
satellite.

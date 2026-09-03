# PETRA Phase 10 Legacy Runtime Dependency Audit

## Context

Issue: #228

Phase: 10 — first controlled historical runtime deletion.

Audit foundation: `cb889ed3c202a2e103df94b206a0b78c962fc6d0`

Implementation foundation after prerequisite #229 / PR #232: `36e0f33c905f6ebb1ab19ffa518e1b38b90ffd52`

Verdict: `READY_FOR_FIRST_CONTROLLED_DELETION`

Decision: `GO: DELETE FROZEN LEGACY LEAF`

The sole normative PETRA semantic authority remains
`docs/reference/SPEC.md`.

This audit records removal of one historical PET runtime leaf and its
exclusively coupled historical tests. It does not change PETRA semantics.

## Historical runtime inventory

Common audited source directory: `src/pet/`

The pre-deletion inventory contains exactly 20 Python files:

- `__init__.py`
- `algebra.py`
- `atlas.py`
- `cli.py`
- `core.py`
- `families.py`
- `graph.py`
- `guarded_redirect.py`
- `io.py`
- `lens_api.py`
- `metrics.py`
- `object_metrics.py`
- `object_model.py`
- `operators.py`
- `query.py`
- `rewrite_metric.py`
- `root_base.py`
- `scan.py`
- `structural_route.py`
- `traces.py`

## Runtime dependency classification

| Module | Runtime inbound | Executable inbound | Classification |
| --- | --- | ---: | --- |
| `pet.__init__` | none | 21 | `LEAF_RUNTIME`, `TOOL_COUPLED`, `DEFER` |
| `pet.algebra` | `cli`, `families`, `metrics` | 4 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.atlas` | `cli` | 1 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.cli` | `__init__`, `rewrite_metric` | 3 | `INTERNAL_CORE`, `DEFER` |
| `pet.core` | 13 runtime modules | 25 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.families` | `cli` | 1 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.graph` | `__init__`, `structural_route`, `traces` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.guarded_redirect` | `cli` | 2 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.io` | `__init__`, `cli`, `query`, `scan` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.lens_api` | none | 2 tests | `LEAF_RUNTIME`, `TEST_ONLY_LEAF`, `DELETE_CANDIDATE` |
| `pet.metrics` | `cli` | 1 | `INTERNAL_CORE`, `DEFER` |
| `pet.object_metrics` | `__init__` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.object_model` | 7 runtime modules | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.operators` | `__init__`, `graph`, `traces` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.query` | `cli` | 1 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.rewrite_metric` | `cli` | 4 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.root_base` | `__init__` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.scan` | `cli` | 0 | `INTERNAL_CORE`, `DEFER` |
| `pet.structural_route` | `cli` | 1 | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.traces` | `__init__`, `structural_route` | 0 | `INTERNAL_CORE`, `DEFER` |

The static audit established:

`src/petra` has no dependency on `pet`.

No canonical PETRA runtime, operator, serializer, package export, or CLI is
affected by the selected deletion.

## Runtime import graph

Pre-deletion runtime edges were:

- `pet.__init__` → `cli`, `core`, `graph`, `io`, `object_metrics`,
  `object_model`, `operators`, `root_base`, `traces`
- `pet.algebra` → `core`
- `pet.atlas` → none
- `pet.cli` → `algebra`, `atlas`, `core`, `families`, `guarded_redirect`,
  `io`, `metrics`, `query`, `rewrite_metric`, `scan`, `structural_route`
- `pet.core` → none
- `pet.families` → `algebra`, `core`
- `pet.graph` → `core`, `object_model`, `operators`
- `pet.guarded_redirect` → none
- `pet.io` → `core`
- `pet.lens_api` → none
- `pet.metrics` → `algebra`, `core`
- `pet.object_metrics` → `object_model`
- `pet.object_model` → `core`
- `pet.operators` → `core`, `object_model`
- `pet.query` → `core`, `io`
- `pet.rewrite_metric` → `cli`, `core`
- `pet.root_base` → `core`, `object_model`
- `pet.scan` → `core`, `io`
- `pet.structural_route` → `graph`, `object_model`, `traces`
- `pet.traces` → `graph`, `object_model`, `operators`

## Candidate leaf ranking

Only two modules had zero runtime inbound dependencies.

1. `pet.lens_api`
   - zero runtime inbound dependencies;
   - zero runtime outbound dependencies;
   - zero PETRA dependency;
   - exactly two executable inbound references;
   - both executable references are dedicated historical tests;
   - no tool or wrapper importer.

2. `pet.__init__`
   - zero runtime inbound dependencies;
   - 21 executable inbound references;
   - broad test and research-tool coupling;
   - therefore deferred.

`pet.lens_api` has the smallest demonstrated deletion blast radius.

## Selected first controlled cluster

Selected runtime leaf:

- `pet.lens_api`

Exclusively coupled historical tests:

- `tests/test_lens_api_contract.py`
- `tests/test_lens_api_ocf_compat.py`

Exclusively coupled wrappers:

- none

The deletion introduces no replacement module, compatibility bridge, alias,
shim, skip, xfail, marker change, or CI exclusion.

## Documentation boundary

Historical and research documents remain evidence, not maintained PETRA
semantics.

In particular, `docs/research/pet_lens_api.md` remains as historical material.
Its retention does not require preservation of the deleted runtime API.

Git history, tags, releases, and explicitly historical/research documents are
the preservation mechanism for obsolete PET behavior.

The documentation validator is not weakened to accommodate this deletion.

## Explicit deferrals

Later Phase 10 slices retain ownership of:

- the remaining 19 historical PET runtime files;
- their coupled historical runtime tests;
- PET graph/path/trace/metrics/projection surfaces;
- historical CLI behavior;
- tools/core importers;
- tools/classic importers;
- tools/legacy importers;
- tools/research importers;
- remaining wrappers and stale active surfaces;
- repository rename;
- PETRA release-line publication.

No deferred concern is silently promoted into this deletion.

## Verification plan

The deletion gate requires:

- focused PETRA distribution/CLI boundary tests;
- canonical PETRA regression tests;
- full `pytest -q -m "not slow"` regression;
- documentation consistency;
- `git diff --check`;
- static proof that `src/petra` does not import `pet`;
- proof that no retained Python file imports `pet.lens_api`;
- exact changed-surface verification.

## Non-claims

This work does not claim that:

- deletion of the entire historical PET runtime is complete;
- the remaining PET runtime files are independently safe to delete;
- Phase 9 derived layers are promoted;
- sparse-image research is advanced;
- PETRA VISION is advanced;
- historical PET behavior is PETRA behavior;
- PETRA semantics have changed.

The result establishes only the repeatable Phase 10 pattern:

audit → freeze one real leaf → delete only its exclusive surface → run full
regression → repeat.

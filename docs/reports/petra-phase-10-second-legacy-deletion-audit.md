# PETRA Phase 10 Second Legacy Deletion Audit
<!-- docs-check: allow-stale-src-refs -->

## Context

Issue: #234

Phase: 10 — second controlled historical runtime deletion.

Foundation:

`fd8037fbee6a5e45882c74559b0482117bdad54f`

Verdict:

`READY_FOR_SECOND_CONTROLLED_DELETION`

Decision:

`GO: DELETE SECOND FROZEN LEGACY CLUSTER`

The sole normative PETRA semantic authority remains
`docs/reference/SPEC.md`.

This audit concerns historical PET migration residue only. It does not change
PETRA semantics.

## Current historical runtime inventory

Common audited source directory: `src/pet/`

The pre-deletion inventory contains exactly 19 Python files:

- `__init__.py`
- `algebra.py`
- `atlas.py`
- `cli.py`
- `core.py`
- `families.py`
- `graph.py`
- `guarded_redirect.py`
- `io.py`
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

## Graph delta since the first deletion

Issue #228 / PR #233 deleted `pet.lens_api`.

That module had no runtime import edges, so its physical removal did not
otherwise restructure the surviving graph.

The second audit corrects two important dependency interpretations:

1. `pet.__init__` is not an ordinary safe leaf. Importing `pet` or any
   `pet.<submodule>` executes package initialization, so the package initializer
   remains broadly coupled to historical tests and tools.
2. `pet.cli` has a lazy executable dependency on `pet.rewrite_metric` through
   the historical `rewrite` command. Removing the runtime module therefore
   requires removal of that command branch in the same controlled cluster.

`src/petra` has no dependency on `pet`.

## Current runtime import graph

- `__init__` → `cli`, `core`, `graph`, `io`, `object_metrics`,
  `object_model`, `operators`, `root_base`, `traces`
- `algebra` → `core`
- `atlas` → none
- `cli` → `algebra`, `atlas`, `core`, `families`, `guarded_redirect`, `io`,
  `metrics`, `query`, `rewrite_metric`, `scan`, `structural_route`
- `core` → none
- `families` → `algebra`, `core`
- `graph` → `core`, `object_model`, `operators`
- `guarded_redirect` → none
- `io` → `core`
- `metrics` → `algebra`, `core`
- `object_metrics` → `object_model`
- `object_model` → `core`
- `operators` → `core`, `object_model`
- `query` → `core`, `io`
- `rewrite_metric` → `cli`, `core`
- `root_base` → `core`, `object_model`
- `scan` → `core`, `io`
- `structural_route` → `graph`, `object_model`, `traces`
- `traces` → `graph`, `object_model`, `operators`

## Package initialization and export coupling

`src/pet/__init__.py` exports historical core, IO, object-model,
object-metrics, root-base, operator, graph, and trace symbols.

It does not export `rewrite_metric`.

The package initializer remains broadly coupled because every executable
`pet` or `pet.<submodule>` import executes it. It is therefore explicitly
deferred.

## Module classification

| Module | Classification |
| --- | --- |
| `pet.__init__` | `PACKAGE_INIT_COUPLED`, `TOOL_COUPLED`, `DEFER` |
| `pet.algebra` | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.atlas` | `TOOL_COUPLED`, `DEFER` |
| `pet.cli` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `TOOL_COUPLED`, `DEFER` |
| `pet.core` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `TOOL_COUPLED`, `DEFER` |
| `pet.families` | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.graph` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.guarded_redirect` | `TOOL_COUPLED`, `DEFER` |
| `pet.io` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.metrics` | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.object_metrics` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.object_model` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.operators` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.query` | `TOOL_COUPLED`, `DEFER` |
| `pet.rewrite_metric` | `TOOL_COUPLED`, `DELETE_CANDIDATE` |
| `pet.root_base` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |
| `pet.scan` | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.structural_route` | `INTERNAL_CORE`, `TOOL_COUPLED`, `DEFER` |
| `pet.traces` | `INTERNAL_CORE`, `PACKAGE_INIT_COUPLED`, `DEFER` |

No remaining module is merely `DOC_ONLY_REFERENCE`.

## Candidate ranking

Current ranking by demonstrated deletion blast radius:

1. `pet.rewrite_metric` — selected;
2. `pet.atlas` — deferred because of CLI/tool/report coupling;
3. `pet.guarded_redirect` — deferred because of structural-factorization and
   research/tool coupling;
4. `pet.query`, `pet.families`, and `pet.scan` — deferred because of CLI and
   workflow coupling;
5. package-exported core/graph/object/operator/root/trace/IO modules — deferred
   because of package initialization/export and runtime fanout.

## Selected second controlled cluster

Selected historical runtime:

- `pet.rewrite_metric`

The cluster also removes the exclusively coupled PET-METICA command,
tests, research probes, and root wrappers.

The runtime module is not part of PETRA, is not exported by `pet.__init__`,
and is not required by `src/petra`.

### Historical tests removed

- `tests/test_cli_rewrite.py`
- `tests/test_rewrite_transport_compose_v1.py`
- `tests/test_metica_range_sweep.py`
- `tests/test_metica_seven_family_probe.py`

### Historical test narrowed

`tests/test_tools_pet_lens_transition.py` retains its immediate-transition and
pipeline coverage. Only the multistep rewrite-fallback test is removed.

### Historical wrappers/probes removed

- `tools/pet_rewrite_metric.py`
- `tools/pet_metica_range_sweep.py`
- `tools/pet_metica_seven_family_probe.py`
- `tools/research/pet_rewrite_metric.py`
- `tools/research/pet_metica_range_sweep.py`
- `tools/research/pet_metica_seven_family_probe.py`

### Narrow legacy adjustments

`src/pet/cli.py` loses only the historical `rewrite` parser family and its
dispatch branch.

`tools/legacy/pet_lens_transition.py` retains immediate transition discovery
from the historical `compare` and `explain` commands but no longer falls back
to PET-METICA multistep rewrite traversal.

No `src/pet/__init__.py` change is required.

## Explicit deferrals

This slice does not remove or retarget:

- the remaining historical PET package initializer;
- the remaining historical PET CLI;
- core/factorization behavior;
- graph/path/trace facilities;
- object model or operators;
- metrics;
- query/families/scan;
- guarded redirect;
- structural route;
- retained lens-transition immediate behavior;
- independent shape-rewrite arithmetic tooling;
- repository rename;
- PETRA release-line publication.

## Verification plan

Acceptance requires:

- retained lens-transition focused tests;
- independent shape-rewrite arithmetic focused tests;
- PETRA distribution/CLI boundary tests;
- canonical PETRA regression;
- complete non-slow regression in a CI-equivalent editable-install
  environment with CI-style `PATH`;
- documentation consistency;
- `git diff --check`;
- static proof that `src/petra` imports no `pet`;
- proof that no retained executable importer or CLI command requires
  `pet.rewrite_metric`;
- exact changed-surface verification.

## Non-claims

This work does not claim that:

- the historical PET runtime is fully deleted;
- PET-METICA becomes PETRA semantics;
- graph, paths, traces, metrics, or numeric projection are promoted;
- sparse-image research is advanced;
- PETRA VISION is advanced;
- repository rename or release publication is complete;
- every remaining PET module is independently safe to delete.

The result establishes the second repetition of the Phase 10 pattern:

current dependency audit → freeze one inseparable historical cluster → remove
only that cluster → full regression → repeat.

# PETRA Phase 10 — Scan/Query Slice Audit
<!-- docs-check: allow-stale-src-refs -->

## Context

Issue: #228 (predecessors), new slice.

Phase: 10 — third controlled historical runtime deletion.

Verdict: `READY_FOR_SCAN_QUERY_SLICE`

Decision: `GO: DELETE SCAN AND QUERY SUBSYSTEM`

The sole normative PETRA semantic authority remains
`docs/reference/SPEC.md`.

This audit records the coordinated removal of the historical scan and
query subsystem: their runtime modules, their CLI surface, their tools,
their canonical test coverage, and their report contract.

## Scope of this slice

The scan/query subsystem comprises two coupled runtime modules:

- `pet.scan` — writes a JSONL dataset from a range of integers;
- `pet.query` — reads a JSONL dataset and answers structural queries
  (filter, group-count, same-shape, same-signature, signature-family,
  generator-family).

They are coupled: `pet.query` consumes the format that `pet.scan`
produces. Removing one without the other leaves an incomplete subsystem
and contradictory documentation. They must go together.

## Historical runtime inventory

Common audited source directory: `src/pet/`

The pre-deletion inventory contains exactly 18 Python files:

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
- `root_base.py`
- `scan.py`
- `structural_route.py`
- `traces.py`

(`lens_api.py` and `rewrite_metric.py` were removed in earlier slices.)

## Selected deletion surface

### Runtime modules (2 files)

- `src/pet/scan.py` — 36 lines
- `src/pet/query.py` — 416 lines

### Tools (2 files)

- `tools/scan_query.py` — root wrapper (17 lines)
- `tools/research/scan_query.py` — implementation (8 lines)

### Tests (4 files)

- `tests/test_scan_jsonl_schema.py`
- `tests/test_scan_query.py`
- `tests/test_cli_query.py`
- `tests/test_atlas_summary.py`

Total: 17 tests currently collected under the canonical gate.

### CLI surface (5 removal points in `src/pet/cli.py`)

1. Line 30: `from .query import register_subparser as register_query_subparser, run_args as run_query`
2. Lines 6707–6711: the `scan` subparser
3. Line 7038: `register_query_subparser(subparsers)`
4. Lines 7621–7630: the `scan` dispatch branch
5. Lines 8254–8255: the `query` dispatch branch

## Documentation surface

The following documents reference `pet scan` as an active command and
must be treated as historical after this slice:

- `docs/reports/generated/atlas-2-100000.md`
- `docs/reports/generated/atlas-2-1000000.md`
- `docs/reports/generated/metrics-2-10000.md`
- `docs/reports/generated/signatures-catalog-2-1000000.md`
- `docs/reports/process/canonical-workflow.md`
- `docs/reports/process/contributor-operator.md`

These reports remain on disk as bounded historical evidence. Their
reproduction commands no longer work; this is expected and documented
rather than fixed.

## Report contract update

`tests/test_report_contracts.py` enforces that specific reports cite
`python3 -m src.pet.cli scan` and `docs/reports/data/scan-`. After this
slice those commands do not exist.

The report contracts must be updated to distinguish:

- **active bounded reports** with regenerable commands;
- **historical bounded reports** retained as evidence, whose commands
  reference a runtime that has been removed.

The four scan-backed reports move to the historical category. The
families-benchmark report remains active.

## The `legacy` marker gap

The four test files in this slice are named `test_scan_*`,
`test_cli_query*`, and `test_atlas_summary*`. They do not match the
`legacy` marker pattern in `tests/conftest.py`, and they do not import
from `pet` directly — they invoke the CLI through `subprocess.run`.

Consequence: they are currently collected under the canonical gate
(`-m "not slow and not legacy"`) even though they exercise only the
historical runtime.

This is a pre-existing marker gap. It is not introduced by this slice,
but it is exposed by it. Two mitigations are possible:

- **A.** Add the four filenames explicitly to the legacy list in
  `tests/conftest.py`.
- **B.** Extend `_is_legacy` to mark any test whose source mentions
  `"pet.cli"` or `"src.pet.cli"` inside a `subprocess.run` call.

Option A is the minimum viable fix and is applied in this slice.

Option B is left as a follow-up for a separate marker-strategy audit.

## Runtime dependency graph (post-slice)

After removal of `pet.scan` and `pet.query`, the remaining runtime
import edges are:

- `pet.__init__` → `cli`, `core`, `graph`, `io`, `object_metrics`,
  `object_model`, `operators`, `root_base`, `traces`
- `pet.algebra` → `core`
- `pet.atlas` → none
- `pet.cli` → `algebra`, `atlas`, `core`, `families`, `guarded_redirect`,
  `io`, `metrics`, `structural_route`
- `pet.core` → none
- `pet.families` → `algebra`, `core`
- `pet.graph` → `core`, `object_model`, `operators`
- `pet.guarded_redirect` → none
- `pet.io` → `core`
- `pet.metrics` → `algebra`, `core`
- `pet.object_metrics` → `object_model`
- `pet.object_model` → `core`
- `pet.operators` → `core`, `object_model`
- `pet.root_base` → `core`, `object_model`
- `pet.structural_route` → `graph`, `object_model`, `traces`
- `pet.traces` → `graph`, `object_model`, `operators`

No canonical PETRA runtime, operator, serializer, package export, or CLI
is affected by this deletion.

## Verification plan

The slice is accepted only when:

1. no Python file outside `src/pet/` imports `pet.scan` or `pet.query`;
2. no tool imports `pet.scan` or `pet.query`;
3. the canonical gate passes:
   `pytest -q -m "not slow and not legacy"`;
4. `test_report_contracts.py` passes with the updated contract table;
5. `docs-check` passes;
6. `git diff --check` is clean;
7. `src/petra` still has no dependency on `pet`.

## What this slice does not remove

- `pet.atlas` and `tools/research/atlas_summary.py` remain. They read
  generic JSONL and do not depend on `pet.scan` or `pet.query`.
- The four historical scan-backed reports remain on disk. They are
  evidence, not active surfaces.
- The rest of the historical runtime (`core`, `cli`, `algebra`,
  `families`, `metrics`, `object_model`, `operators`, `graph`, `traces`,
  `structural_route`, `guarded_redirect`, `atlas`, `io`, `root_base`,
  `__init__`) remains. Further slices will be audited separately.

## Non-claims

This work does not claim that:

- the historical PET runtime is fully deleted;
- the marker-gap problem is closed (only mitigated for these files);
- the remaining runtime modules are independently safe to delete;
- PETRA semantics have changed;
- any historical report is now regenerable.

The result establishes the third repetition of the Phase 10 pattern:

current dependency audit → freeze one inseparable historical cluster →
remove only that cluster → full regression → repeat.

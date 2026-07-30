# PET module stability classification

This document classifies the tracked Python modules under `src/pet` by stability
level and architectural role.

The goal is to make the repository easier to reason about after the
first-principles implementation audit.

This is a classification document, not a refactoring plan.

It does not change implementation behavior.

> **Implementation-compatibility boundary.** `NEW`, `DROP`, `INC`, and `DEC`
> in this classification name current retained value-level implementation
> behavior, not canonical PET semantics. The sole normative future contract is
> [`pet-peg-2.0-object-native-operators.md`](pet-peg-2.0-object-native-operators.md).

## Basis

This classification is based on:

- the tracked module inventory under `src/pet`
- the first-principles implementation audit
- current documentation references
- the current distinction between PET-Base, first-principles PET, PET/PEG 2.0,
  PET-Metrics, PET-METICA, routing, and research tooling

The categories below are intentionally conservative.

A module classified as research, experimental, or unclear should not be deleted,
rewritten, or promoted without a separate focused audit.

## Stability categories

### Stable machine core

Stable machine core modules define the current PET-Base implementation contract
or the closest implementation of that contract.

These modules are the safest reference point for current stable behavior.

### Stable support

Stable support modules provide infrastructure used by stable behavior, but they
do not define PET semantics by themselves.

### Object-native PET/PEG layer

Object-native modules implement the richer PET/PEG 2.0 object model and related
operations.

These modules are useful and important, but they are richer than the minimal
first-principles notation and should not be confused with the stable PET-Base
tree/JSON contract.

### Active research and analysis tooling

These modules support scans, analysis, exploratory metrics, reports, shape
operations, or rewrite experiments.

They may be useful and well-tested, but they are not automatically foundational.

### Experimental routing and advisory tooling

These modules support routing, guarded redirect, advisory workflows, or similar
higher-level behavior.

They should remain clearly separated from PET-Base semantics.

### Mixed command hub

Mixed command hubs expose many layers at once.

They are useful interfaces, but they should not be treated as semantic sources
of truth.

## Module table

| Module | Stability category | Architectural role | Notes |
|---|---|---|---|
| `core.py` | stable machine core | legacy PET-Base tree implementation | Defines the compact PET tree representation, `encode(n)`, `decode(tree)`, validation, and canonical metrics for the current `N >= 2` machine-facing contract. |
| `io.py` | stable support | JSON and rendering helpers | Supports serialization and display behavior. It should not define PET semantics independently. |
| `__init__.py` | stable support | package entry support | Infrastructure only. |
| `object_model.py` | object-native PET/PEG layer | recursive PET object model | Supports `pet_object_from_int(1)` and richer object identity, roles, addresses, and metadata. It is broader than PET-Base JSON. |
| `object_metrics.py` | object-native PET/PEG layer | metrics bridge for PET objects | Computes metrics over `PETObject`; bridges legacy-compatible metrics and object-native structure. |
| `root_base.py` | object-native PET/PEG layer | exact and partial root-base recursion | Useful PET/PEG 2.0 extension, not first-principles core. |
| `operators.py` | object-native PET/PEG layer | NEW/DROP/INC/DEC operator semantics | Current operators mutate represented integer value and rebuild objects; not yet pure structural internal rewrites. |
| `graph.py` | object-native PET/PEG layer | graph nodes, edges, paths, traversal | Downstream from object structure. Useful for path studies, not PET-Base definition. |
| `traces.py` | object-native PET/PEG layer | traces and replay certificates | Records and verifies replay of what happened; does not claim route optimality or usefulness. |
| `metrics.py` | active research and analysis tooling | extended metrics and classifiers | Needs separate audit against first-principles `height`, `support`, and canonical metrics. |
| `algebra.py` | active research and analysis tooling | shape and distance operations | Research-facing shape operations. Should not be treated as PET-Base semantics. |
| `atlas.py` | active research and analysis tooling | shape atlas and visualization support | Dataset and analysis support. |
| `families.py` | active research and analysis tooling | integer-family experiments | Useful for bounded family analysis, not core semantics. |
| `scan.py` | active research and analysis tooling | scan records and dataset generation | Supports empirical workflows. Its stable output contract should be judged separately from research interpretation. |
| `query.py` | active research and analysis tooling | JSONL and dataset query operations | Tooling layer for generated data, not PET definition. |
| `rewrite_metric.py` | active research and analysis tooling | rewrite graph and distance experiments | PET-METICA-facing research module. Bounded empirical findings should not be presented as general theorems. |
| `structural_route.py` | experimental routing and advisory tooling | structural route command backend | Higher-level route/tooling layer. Not first-principles core. |
| `guarded_redirect.py` | experimental routing and advisory tooling | guarded redirect backend | Experimental routing support promoted to package code. Requires separate audit before any stronger stability claim. |
| `lens_api.py` | experimental routing and advisory tooling | optional PET lens advisory API | Useful integration surface, but not PET-Base semantics. |
| `cli.py` | mixed command hub | command-line interface across many layers | Very large and mixed. It exposes stable, research, routing, and historical behavior. It must not be treated as the source of truth for PET semantics. |

## Current architectural reading

The repository currently has one stable machine-facing PET-Base core:

- `core.py`

It also has a richer object-native PET/PEG implementation layer:

- `object_model.py`
- `object_metrics.py`
- `root_base.py`
- `operators.py`
- `graph.py`
- `traces.py`

Research and analysis workflows live mostly in:

- `metrics.py`
- `algebra.py`
- `atlas.py`
- `families.py`
- `scan.py`
- `query.py`
- `rewrite_metric.py`

Routing and advisory workflows live mostly in:

- `structural_route.py`
- `guarded_redirect.py`
- `lens_api.py`

The CLI crosses all of these boundaries and should be treated as an interface,
not a semantic definition.

## Rules of engagement

### Do not delete by category

A research or experimental classification is not a deletion marker.

It only means the module should not be promoted, rewritten, or used as a source
of truth without a separate focused audit.

### Do not promote by accident

A module should not become part of the stable PET-Base contract simply because a
CLI command exposes it.

Stability must be documented explicitly.

### Keep PET-Base and PET/PEG separate

`core.py` defines the current stable PET-Base tree/JSON contract.

`object_model.py` and related PET/PEG modules define a richer object-native
layer.

Both can coexist, but they must not be silently merged in documentation or API
design.

### Treat bounded experiments as bounded

Scan results, rewrite paths, hub/friction observations, and family comparisons
may be useful.

They should remain explicitly bounded unless a separate proof or stability
argument exists.

## Known follow-up work

The following follow-ups are intentionally not solved here:

1. Audit `metrics.py` against first-principles `height`, `support`, and
   canonical metrics.
2. Decide whether first-principles API aliases such as `collapse`, `support`,
   and `height` should be exposed.
3. Audit the large mixed `cli.py` surface and classify commands by stability.
4. Add lightweight documentation consistency checks.
5. Review stale documentation references, such as historical paths that no
   longer match the current `src/pet` package layout.

## Summary

The repo should currently be read as layered architecture:

1. stable PET-Base machine representation
2. first-principles conceptual model
3. PET/PEG object-native layer
4. metrics and scan tooling
5. PET-METICA and research experiments
6. routing, advisory, and mixed CLI workflows

This classification keeps the project useful without pretending that every
module has the same stability level.

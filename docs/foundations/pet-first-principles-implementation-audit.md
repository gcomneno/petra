# PET first-principles implementation audit

This document audits the current PET implementation against the first-principles
model defined in:

- `pet-first-principles.md`
- `pet-first-principles-examples.md`
- `pet-notation-collapse.md`

The goal is classification, not refactoring.

This audit does not change implementation behavior.

## Audit basis

This audit is based on:

- the tracked module inventory under `src/pet`
- AST-level class/function inventory for all tracked package modules
- focused source inspection of the current legacy PET core, object model,
  object metrics, root-base layer, operator layer, graph layer, and trace layer

Some research/tooling modules are classified by module name, public function
inventory, and current role in the repository rather than full line-by-line
semantic review.

Those modules should be audited separately before any rewrite, deletion, or API
promotion decision.

## First-principles concepts

The current first-principles model defines:

- `PET(1)` as the leaf object
- canonical `PET(n)` when prime-exponent structure is known
- `collapse(P)` as numeric evaluation
- `support(P)` as the current-level prime-root set
- `height(P)` as recursive exponent-object height
- numeric equality by collapsed value
- structural equality by recursive PET object shape
- the construction boundary: building `PET(n)` from an opaque integer does not avoid factorization cost

## High-level finding

The repository currently has two PET cores:

1. `src/pet/core.py`
   - legacy PET tree representation
   - compact and close to the original recursive prime-exponent encoding
   - does not encode `PET(1)` as a first-class object

2. `src/pet/object_model.py`
   - PET/PEG 2.0 recursive object model
   - supports `n >= 1`
   - represents `1` as a root composite object with no children
   - adds addresses, roles, identity keys, and object metadata

This split is not necessarily wrong.

However, it must be made explicit because the first-principles model now treats
`PET(1)` as part of the foundation, while the legacy tree model starts at
`n >= 2`.

## Module classification

| Module | Classification | First-principles mapping | Notes |
|---|---|---|---|
| `core.py` | legacy PET core | `encode(n)`, `decode(tree)`, metrics | Closest to original compact PET tree, but `encode(n)` requires `n >= 2` and uses `None` as exponent leaf. |
| `object_model.py` | PET/PEG 2.0 object core | recursive objects, addresses, structural identity | Supports `pet_object_from_int(1)` as an empty root object; richer than first-principles notation. |
| `object_metrics.py` | object-native metrics bridge | height, node count, leaf count, recursive mass | Computes legacy-compatible metrics over `PETObject`; `height` of the empty root is `0`. |
| `root_base.py` | PET/PEG 2.0 extension | root-base recursion | Studies `N = R^k`; useful but not first-principles core. |
| `operators.py` | PET/PEG 2.0 extension | operator semantics | Applies operators by represented integer value and rebuilds `PETObject`; not yet pure structural internal rewrite. |
| `graph.py` | PET/PEG 2.0 extension | graph traversal over PET object states | Models paths and operator-produced edges; not first-principles core. |
| `traces.py` | PET/PEG 2.0 extension | traces and certificates | Records and replays what happened; does not claim route quality. |
| `metrics.py` | legacy/research metrics | structural measurements | Needs separate audit for exact relationship to first-principles `height`, support, and structure. |
| `algebra.py` | research/tooling | shape and distance operations | Likely outside first-principles core. |
| `atlas.py` | research/tooling | shape atlas and visualization | Likely dataset/analysis support, not core semantics. |
| `families.py` | research/tooling | integer-family experiments | Outside first-principles core. |
| `query.py` | research/tooling | JSONL/dataset query operations | Outside first-principles core. |
| `scan.py` | research/tooling | scan records | Outside first-principles core. |
| `rewrite_metric.py` | research/tooling | rewrite graph/distance experiments | Outside first-principles core. |
| `structural_route.py` | routing/tooling | structural route command backend | Not first-principles core; likely later experimental/routing layer. |
| `guarded_redirect.py` | routing/tooling | guarded redirect backend | Not first-principles core; recent experimental routing support promoted to package code. |
| `lens_api.py` | advisory integration API | optional PET lens advisory | Stable API surface, but not first-principles core. |
| `io.py` | infrastructure | JSON/rendering helpers | Support module. |
| `cli.py` | interface and historical command hub | exposes many layers | Very large and mixed; should not be treated as core semantics. |
| `__init__.py` | package entry | CLI forwarding | Infrastructure. |

## Detailed notes

### `core.py`

`core.py` defines the legacy PET tree representation:

    PETExp = Union[None, "PET"]
    PETNode = Tuple[int, PETExp]
    PET = List[PETNode]

In this model:

- a node is `(prime, exponent_repr)`
- `None` represents exponent `1`
- a nested list represents a recursive exponent object
- `encode(n)` builds a canonical tree for `n >= 2`
- `decode(tree)` evaluates the tree back to an integer

First-principles mapping:

| First-principles concept | `core.py` mapping |
|---|---|
| canonical `PET(n)` | `encode(n)` for `n >= 2` |
| leaf exponent `PET(1)` | represented implicitly by `None` |
| `collapse(P)` | `decode(tree)` |
| height | `height(tree)` |
| construction boundary | `encode(n)` calls `prime_factorization(n)` |

Important boundary:

`core.py` does not represent `PET(1)` as a standalone tree object. It represents
leaf exponent `1` implicitly as `None`.

This is legacy-compatible, but it differs from the new first-principles docs
where `PET(1) = 1` is explicit.

### `object_model.py`

`object_model.py` defines the PET/PEG 2.0 recursive object model.

The central type is `PETObject`, which records:

- `value`
- `role`
- `kind`
- `address`
- `children`
- `prime_label`

`pet_object_from_int(n)` accepts `n >= 1`.

For `n = 1`, it returns a root composite object with no children.

First-principles mapping:

| First-principles concept | `object_model.py` mapping |
|---|---|
| `PET(1)` | `pet_object_from_int(1)` |
| canonical `PET(n)` | `pet_object_from_int(n)` |
| recursive exponent objects | child objects built from exponent structure |
| structural equality | `structurally_equivalent(...)` and identity/signature helpers |
| addresses | object addresses such as `()` and `(2,)` |

Important boundary:

`PETObject` is richer than first-principles PET notation. It includes address,
role, kind, and concrete value metadata. That makes it suitable for PET/PEG 2.0,
but it should not be confused with the minimal notation itself.

### `object_metrics.py`

`object_metrics.py` computes metrics directly from `PETObject`.

It is a bridge between:

- legacy metrics from `core.py`
- PET/PEG 2.0 object-native structure

Important alignment:

`pet_object_height(pet_object_from_int(1))` uses no metric roots and returns
`0`, matching the first-principles convention:

    height(PET(1)) = 0

### `root_base.py`

`root_base.py` is an extension layer.

It studies exact root-base decomposition:

    N = R^k

where `R` can itself be represented as a PET/PEG object.

This is valuable for PET/PEG 2.0, but it is not required to define the
first-principles model.

### `operators.py`

`operators.py` is an operator-semantics layer.

It defines target resolution for operators such as:

- `NEW`
- `DROP`
- `INC`
- `DEC`

Important implementation note:

Operator application currently mutates by represented integer value and then
rebuilds a `PETObject`.

Therefore it should be classified as PET/PEG 2.0 operator semantics, not as a
pure first-principles structural rewrite core.

### `graph.py`

`graph.py` models PET/PEG graph nodes, edges, paths, and bounded traversal over
operator applications.

This belongs to the path/traversal layer.

It is downstream from the first-principles object model.

### `traces.py`

`traces.py` records and checks traces.

Its own docstrings state the important boundary:

- a trace records what happened
- a certificate verifies replay
- neither one claims route quality

This aligns well with the new foundation boundary against overclaiming.

## Risks and mismatches

### 1. Dual core representation

The project has both:

- legacy tree PET in `core.py`
- PET/PEG 2.0 object PET in `object_model.py`

This is manageable, but only if the distinction remains explicit.

### 2. `PET(1)` mismatch

The first-principles docs define:

    PET(1) = 1

`object_model.py` supports this through `pet_object_from_int(1)`.

`core.py` does not support `encode(1)` and instead uses `None` as an implicit
leaf exponent.

This is the most important semantic mismatch found so far.

### 3. Collapse naming mismatch

The first-principles docs use:

    collapse(P)

The legacy implementation uses:

    decode(tree)

This is functionally aligned, but the naming may obscure the conceptual mapping.

No rename is recommended in this audit.

### 4. CLI is too mixed to be considered core

`cli.py` contains stable commands, research commands, opaque probes, routing
logic, cache handling, and historical experiments.

It should not be used as the source of truth for first-principles PET semantics.

### 5. Research layers should not be mistaken for foundation

Modules such as `guarded_redirect.py`, `structural_route.py`,
`rewrite_metric.py`, `scan.py`, `families.py`, and `atlas.py` may be useful, but
they are not first-principles PET definitions.

## Recommendation

Do not rewrite the repository yet.

The safest next step is to preserve the current implementation and document the
semantic split clearly:

- `core.py` is the legacy compact PET tree implementation.
- `object_model.py` is the PET/PEG 2.0 object-native implementation.
- `object_metrics.py` bridges metrics between the two.
- routing, graph, traces, and guarded redirect belong to later layers.

Possible future issue:

    Define explicit first-principles API aliases

That issue could consider whether package code should expose names like:

- `canonical_pet(n)`
- `collapse(obj)`
- `support(obj)`
- `height(obj)`

but this audit does not propose that change directly.

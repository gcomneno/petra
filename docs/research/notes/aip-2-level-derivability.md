# AIP-2 level derivability

## Status

Research note for issue #257 under the parent AIP-2 relation-ontology issue #256.

This note is non-normative. It does not change `docs/reference/SPEC.md`, the
runtime model, public APIs, CLI behavior, canonical serialization, addressing,
operator semantics, or Resolver behavior.

## Hypothesis

`level` and `depth` are structural properties derived from recursive
containment and are not primitive ontological data.

The candidate rule is:

```text
level(root occurrence) = 0
level(child occurrence) = level(parent occurrence) + 1
```

Equivalently, for any occurrence selected by a structural path `p` from the
root, its level is the number of recursive containment steps in `p`.

This makes level a function of an occurrence-in-context rather than an
intrinsic attribute of the subshape object itself.

## What must be shown

The hypothesis is supported only if all of the following hold:

1. every occurrence level is uniquely reconstructible from recursive
   containment;
2. structural equality does not require stored level metadata;
3. validation and normalization do not require stored level metadata;
4. canonical serialization derives nesting from structure rather than reading
   a level field;
5. SPROUT, SHED, GRAFT, and PRUNE do not require an independent level value;
6. Resolver depth measurements are computed from traversal context;
7. no candidate core invariant or rewrite result changes solely because of an
   independent stored level value detached from structural context.

## Model audit

The current runtime model contains `Leaf`, `Container`, `Term`, and `Root`.
There is no `level` or `depth` field on any of these model objects.

A nested occurrence is reached only by recursively following term targets.
Therefore the current executable model already provides an important negative
observation: level information is not stored as part of shape identity.

### Equality

Current structural equality compares shape type, container width, positional
terms, root ranks, and recursively corresponding child shapes. It does not
compare a level field because none exists.

Thus current equality already satisfies the elimination test for explicit
level metadata:

```text
stored level metadata = absent
structural equality   = still fully defined
```

This does not by itself prove level is non-ontological, but it proves current
identity does not need an independently stored level value.

### Validation

`validate_shape()` performs an explicit recursive traversal. It validates the
current node, checks each term rank against its position, and descends into the
term target. The traversal stack records where validation must resume; it does
not read or validate a level attribute.

Canonicality therefore depends on recursive structure and positional rank in
the current v2 model, not on stored depth metadata.

### Normalization

`normalize_shape()` performs a post-order traversal and rebuilds containers
with ranks assigned from local sibling position. It does not attach or consume
level data.

Moving an otherwise equal subshape to another structural depth therefore does
not require rewriting an intrinsic level property inside that subshape.

## Addressing audit

Canonical addresses encode structural traversal as a tuple of child indices.
For a term occurrence addressed by indices

```text
(i0, i1, ..., in)
```

its containment depth is derivable from the number of recursive path segments.
The resolver walks those indices through containers; crossing a `Leaf` fails.
No level field participates in resolution.

This gives an operational reconstruction rule:

```text
term occurrence level = len(address.indices)
```

subject to the convention that the root shape itself is level 0.

A slot marker such as the current `^` suffix changes address kind, not the
number of recursive containment steps. The marker is therefore irrelevant to
level derivability.

Classification:

```text
recursive path         = REPRESENTATION of structural location
path length / level    = DERIVED STRUCTURAL PROPERTY
stored level identity  = absent
```

The path syntax itself is not being promoted to ontology here.

## Operator audit

### SPROUT

SPROUT acts on the root anchor or on a selected nested container. Nestedness is
established by address resolution and recursive reconstruction of the selected
path. No explicit level value is read.

The rewrite effect depends on the selected structural occurrence and its local
container shape, not on a stored depth number.

Result:

```text
explicit stored level required = no
level derivable from target path = yes
```

### SHED

SHED removes an eligible terminal occurrence and rebuilds the recursive owner
path. Top-level versus nested behavior is detected by whether the parent path
is empty:

```text
parent_indices = resolved.address.indices[:-1]
```

Again, this is structural context. There is no independent level field.

Result:

```text
explicit stored level required = no
root/nested distinction         = derived from path structure
```

### GRAFT

GRAFT's default selector searches recursively for the deepest eligible latent
slot. The implementation computes candidate depth as the length of the owner
path while traversing:

```text
depth = len(owner_indices)
```

This is important: GRAFT does depend on a notion of depth for its current
default tie-breaking policy, but that depth is calculated from recursive
containment. It is not stored in the target object.

Therefore the existence of a depth-sensitive default does not establish depth
as primitive ontology. It establishes only that one representation-level or
operational selection policy may use a derived structural metric.

Result:

```text
depth used by current default policy = yes
independent stored level required    = no
```

### PRUNE

PRUNE's default selector likewise traverses recursively and computes depth from
the current path. Explicit PRUNE checks whether the selected occurrence is
nested by inspecting whether a parent owner path exists. It also checks local
singleton-parent structure.

No stored level participates.

Result:

```text
depth/nestedness used       = yes
source                      = current recursive path
stored level required       = no
```

## Serialization audit

The parser bounds nesting with the size of its current open-container frame
stack. When it opens a new container it checks the current number of frames
against `_MAX_NESTING_DEPTH`.

Thus parser depth is computed from parser traversal state:

```text
current parse depth = len(open container frames)
```

The serializer likewise traverses the recursive object structure and can bound
nesting without reading any level property from a model node.

The fixed maximum nesting depth in the public serialization contract is a
resource limit over a derived property. A resource bound on depth does not make
level metadata part of shape identity.

Classification:

```text
nesting depth limit = REPRESENTATION / RESOURCE POLICY over derived structure
stored level        = NOT REQUIRED
```

## Resolver audit

Resolver's `_max_depth()` explicitly demonstrates derivability. It initializes
traversal with:

```text
(shape, 0)
```

and pushes each recursive child as:

```text
(child, level + 1)
```

The maximum observed value is used as a structural lower bound in A* search.
There is no level field on the shape.

This is a constructive witness that maximum depth is computable from recursive
containment alone.

Resolver also enumerates term addresses recursively. Whether an occurrence is
nested and whether its parent is a singleton are derived from traversal
context and local structure, not stored level metadata.

Classification:

```text
max depth metric          = DERIVED STRUCTURAL PROPERTY
A* use of depth           = DERIVED-LAYER ALGORITHM
explicit level primitive  = absent
```

## Occurrence level versus subshape identity

The same structural subshape can occur at different levels in different
contexts without changing its own internal structure.

Schematic example:

```text
A = Terminal
B = Composite({A})
C = Composite({B})
```

An occurrence structurally equal to `A` may appear directly under one
composite or deeper under another. Its level changes because its context/path
changes, not because `A` carries a mutable intrinsic level attribute.

Therefore the correct domain of the level function is not an isolated shape:

```text
level : occurrence-in-a-whole-shape -> N
```

not:

```text
level : shape -> N
```

except for aggregate functions such as maximum depth, which are computed from
the whole recursive shape.

## Elimination test

Imagine enriching every occurrence with redundant metadata:

```text
Occurrence(shape=S, stored_level=k)
```

If `k` is required to equal the number of containment steps from the root,
then it contains no independent information: it can always be recomputed.

If `k` is allowed to disagree with structural depth, one of two things must be
true:

1. the disagreement is invalid redundant metadata; or
2. `k` expresses an additional interpretation-specific notion unrelated to
   recursive containment.

Neither case justifies `stored_level` as primitive abstract PETRA ontology.

## Counterexample criterion

A genuine counterexample would require a candidate core rule `F` such that two
states with the same recursive structure and the same selected structural
occurrence produce different core outcomes solely because of different
independent level metadata.

No such dependency exists in the audited current model:

- equality has no level field;
- validation has no level field;
- normalization has no level field;
- addressing derives depth from path length;
- serialization derives nesting from traversal state;
- all four operators derive root/nested/deepest distinctions from structural
  paths;
- Resolver computes maximum depth during traversal.

Within this audit scope, no counterexample is present.

## Important limitation

This result does not prove that every imaginable future PETRA interpretation
must ignore levels. An interpretation may assign semantic meaning to depth, or
may define a different notion of level altogether.

The claim is narrower:

> Abstract PETRA does not need an independent stored level primitive in order
> to recover recursive containment depth or support the current candidate core
> structural behavior.

An interpretation-specific level system would therefore be additional
semantic structure layered on top of PETRA, not evidence that recursive level
must be primitive in the core.

## Provisional result

The audit supports the issue #257 hypothesis:

```text
recursive containment = CORE candidate
level/depth           = DERIVED CORE PROPERTY
explicit level field  = NOT CORE
```

More precisely:

> The level of an occurrence is uniquely determined by its recursive
> containment path from the root. Current equality, validation, normalization,
> addressing, serialization, all four structural operators, and Resolver do
> not require an independently stored level value.

This is a research conclusion, not a normative SPEC change.

## Consequence for AIP-2

AIP-2 should not model relation ontology by introducing explicit layers or
level-bearing nodes. The next relation question can therefore be reduced to a
cleaner one:

> beyond recursive containment itself, is any additional relation object or
> relation kind intrinsically required by abstract PETRA?

That question remains open under issue #256.

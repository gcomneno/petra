# PET object-native relocation and permutation (bounded research note)

## Status

Bounded research specification.

This note investigates a possible object-native structural relocation family.
It is not part of the stable PET-Base specification and does not extend the
normative object-native operator contract.

The normative foundation remains:

- [`../../reference/SPEC.md`](../../reference/SPEC.md)

That contract deliberately defers symmetric relocation in its follow-up item
“Research specification: object-native symmetric relocation”.

## Research boundary

This note studies relocation inside the future object-native grammar:

```text
PET       ::= Leaf | Container
Leaf      ::= 1
Container ::= Product(Term+)
Term      ::= Root ^ PET
```

It does not define relocation on:

- legacy prime-labelled PET trees;
- current `PETObject.value` or `PETObject.prime_label`;
- integers reconstructed through factorization;
- stable CLI commands;
- current PET-METICA `NEW`, `DROP`, `INC`, or `DEC` behavior.

No relocation rule in this note selects primes, changes represented integers,
or derives an after-shape from an after-value.

## 1. Candidate relocation family

Let `R` denote a possible object-native structural relocation family.

The initial candidate operations are:

```text
SWAP(container, i, j)
PERMUTE(container, permutation)
SCRAMBLE(container, key, nonce, context)
```

Their intended separation is:

| Operation | Role |
| --- | --- |
| `SWAP` | explicit exchange of two positions |
| `PERMUTE` | explicit deterministic reordering of all positions |
| `SCRAMBLE` | secret derivation and application of a permutation |

`SWAP` and `PERMUTE` are structural operations.

`SCRAMBLE` is a policy for selecting a `PERMUTE` mapping. It does not define a
different structural rewrite.

## 2. Ordered-container model

Let a selected container have visible terms:

```text
C(t0, t1, ..., t(n-1))
```

The object-native contract defines a container as owning an ordered, non-empty
sequence of visible terms.

A permutation is represented in this note by a source-order vector:

```text
π = [π0, π1, ..., π(n-1)]
```

Each entry states which pre-rewrite source position occupies the
corresponding after-rewrite destination position. The vector must
contain every integer in `0..n-1` exactly once.

Thus:

```text
π = [2, 0, 1]
```

means:

```text
after position 0 <- before position 2
after position 1 <- before position 0
after position 2 <- before position 1
```

The candidate result is:

```text
PERMUTE(C(t0, ..., t(n-1)), π)
    =
CANONICAL_RANKS(
    C(tπ0, ..., tπ(n-1))
)
```

`CANONICAL_RANKS` does not sort term payloads by structure, value, insertion
history, or any external label.

It assigns current positional roots:

```text
r0, r1, ..., r(n-1)
```

according to the new visible order.

## 3. Root ranks are not persistent identities

Object-native root spellings are state-scoped positional identities.

Therefore:

```text
r0
```

means “the term currently at position zero in this container and shape state”.

It does not mean “the same historical term across rewrites”.

For example:

```text
before:
C(r0^A, r1^B, r2^C)

after permutation [2, 0, 1]:
C(r0^C, r1^A, r2^B)
```

The terms changed position. The ranks were then recomputed from the resulting
visible sequence.

A relocation witness must therefore carry any required before-to-after
correspondence externally. Persistent instance identity must not be inferred
from `r0`, `r1`, or positional addresses.

## 4. SWAP as a transposition

`SWAP(container, i, j)` is the special case of `PERMUTE` induced by the
transposition `τ(i,j)`.

```text
SWAP(P, i, j) = PERMUTE(P, τ(i,j))
```

Candidate preconditions for the initial sibling-only scope:

- the selected target resolves to one container;
- both indices are in range;
- `i != j`;
- exchanging the two selected payloads produces a different canonical
  after-shape.

All direct children are `Term` values and are therefore structurally
compatible for sibling reordering. Cross-container compatibility and
overlapping regions do not arise in this initial scope.

An identity swap or an exchange of payload-equivalent terms is a
canonical no-op and must not be reported as a successful structural
rewrite.

## 5. Observable and collapsed permutations

A material permutation does not always produce a distinct canonical after-shape.

Consider:

```text
P = C(r0^A, r1^A, r2^B)
```

Swapping the first two terms changes their hypothetical historical instances,
but after canonical rank recomputation the observable shape is again:

```text
C(r0^A, r1^A, r2^B)
```

The object-native shape has no persistent identity capable of distinguishing
those two occurrences of `A`.

This note therefore distinguishes:

| Concept | Meaning |
| --- | --- |
| material permutation | permutation over hypothetical pre-rewrite occurrences |
| observable permutation | permutation producing a different canonical shape |
| collapsed permutation | material permutation producing the same canonical shape |

If a container has `n` terms partitioned into structural-equivalence classes
with multiplicities:

```text
m1, m2, ..., mk
```

then the maximum number of observably distinct arrangements is:

```text
n! / (m1! * m2! * ... * mk!)
```

This count concerns observable canonical arrangements, not historical instance
trajectories.

## 6. Address effects

Object-native addresses are positional and belong to one shape state.

Before relocation:

```text
C(r0^A, r1^B, r2^C)

@/0 -> A
@/1 -> B
@/2 -> C
```

After permutation `[2, 0, 1]`:

```text
C(r0^C, r1^A, r2^B)

@/0 -> C
@/1 -> A
@/2 -> B
```

The textual address `@/0` remains syntactically valid but is retargeted.

Consequences:

- pre-rewrite term addresses cannot be treated as persistent object
  identities;
- descendant term and slot addresses must be resolved again in the
  after-shape;
- the selected container address itself remains reusable for the
  immediate inverse because reordering its direct children does not move
  that container;
- this reuse is invalidated if an intervening rewrite changes the
  container or any ancestor path;
- address effects should describe descendant retargeting without
  promising persistent term identity.

## 7. Candidate deterministic invocation

A future deterministic invocation might contain:

```text
schema
operator = "PERMUTE"
target container address
source-order vector
```

The source-order vector must be a total bijection over the selected
container arity.

Candidate stable validation classes include:

- invocation invalid;
- address malformed;
- address out of range;
- address crosses leaf;
- target not container;
- permutation arity mismatch;
- permutation source index out of range;
- permutation contains duplicate source;
- permutation is identity;
- permutation collapses to the original canonical shape.

These names are illustrative and are not stable reason identifiers.

## 8. Candidate result and witness

A successful deterministic relocation result will likely require:

```text
schema
status
operator
invocation_target
resolved_target
before_shape
after_shape
address_effects
reason
inverse_witness
```

The inverse witness must preserve enough information to apply the inverse
relocation to the correct after-shape container.

A candidate witness may include:

```text
algorithm_version
before_shape_commitment
after_shape_commitment
selected_container_address
forward_source_order
inverse_source_order
```

The inverse vector is derived from the forward vector but may be
serialized to make replay explicit and independently verifiable.

The witness is external transformational memory.

It must not silently promote persistent UUID-like identity into the
object-native shape grammar.

## 9. Candidate inverse law

For a valid permutation `π` and its inverse `π^-1`:

```text
PERMUTE(
    PERMUTE(P, π),
    π^-1
) = P
```

This candidate law assumes:

- both operations target the same resolved container;
- no intervening rewrite changes that container or an ancestor path;
- the inverse uses the inverse source-order vector recorded or derived
  from the first result;
- the before and intermediate shape commitments match the replay inputs;
- equality is canonical object-native shape equality.

For a transposition:

```text
SWAP(SWAP(P, i, j), i, j) = P
```

The selected container address must still be resolved against the
after-shape before applying the inverse. In the sibling-only scope it is
expected to select the same container, provided no intervening rewrite
changed that container or an ancestor path.

If payload-equivalent terms collapse the observable permutation to the
original canonical shape, the operation is non-applied. It must not
claim a successful relocation.

## 10. Nested relocation

A relocation target may be:

- the top-level container through the semantic root anchor;
- a materialized exponent container selected through a term address.

Nested relocation raises additional questions:

- confirming that moving a complete term moves its entire exponent
  subtree;
- whether a later relocation family may cross container boundaries;
- which compatibility and overlap rules such a cross-container
  operation needs;
- how an ancestor relocation affects a nested target address;
- whether later cross-container inverse witnesses require additional
  before/after target coordinates.

The conservative initial scope is permutation among direct sibling terms of one
resolved container.

Cross-container relocation is out of scope for the first specification.

## 11. PERMUTE versus SCRAMBLE

`PERMUTE` is deterministic and public:

```text
PERMUTE(P, π)
```

`SCRAMBLE` derives a permutation from secret material:

```text
π = DerivePermutation(key, nonce, context, shape_commitment)

SCRAMBLE(P, key, nonce, context)
    = PERMUTE(P, π)
```

The structural semantics of the result remain those of `PERMUTE`.

A future cryptographic derivation must specify:

- a cryptographically secure pseudorandom generator;
- an unbiased permutation algorithm;
- domain separation;
- algorithm versioning;
- nonce requirements;
- shape/context binding;
- key storage and destruction;
- authenticated witness or commitment handling.

These questions are deliberately deferred until deterministic relocation
semantics are closed.

## 12. Security non-claims

This note does not claim that relocation provides encryption.

A permutation may hide the original association between terms and positions,
but it does not automatically hide:

- term contents;
- recursive shapes;
- term multiplicities;
- container arity;
- structural correlations;
- numeric projections;
- path history;
- recognizable semantic relationships.

`SCRAMBLE` must not be described as encryption without a separate threat model
and security argument.

## 13. Relationship to existing object-native operators

The normative object-native operator pairs are:

| Structural axis | Operators |
| --- | --- |
| width | `SPROUT` / `SHED` |
| depth | `GRAFT` / `PRUNE` |

The candidate relocation family is distinct:

| Structural axis | Candidate operators |
| --- | --- |
| relocation | `SWAP` / `PERMUTE` |

Relocation changes neither width nor depth when it only reorders direct sibling
terms.

It changes positional association, rank assignment, and address resolution.

`SCRAMBLE` belongs above this structural family as a permutation-selection
policy.

## 14. Implementation dependencies

No implementation should be proposed before the object-native foundations
listed in the normative contract exist:

1. immutable object-native shape representation;
2. positional address resolver;
3. structural rewrite engine and versioned result schema.

Relocation may additionally depend on:

- canonical shape serialization;
- shape commitments;
- address-effect comparison;
- shape-native traces and certificates;
- explicit no-op prevention.

The current legacy `PETObject` bridge is not an implementation substrate for
this family.

## 15. Initial implementation non-goals

The first relocation implementation should not include:

- cryptographic key management;
- CSPRNG selection;
- CLI exposure;
- legacy integer reconstruction;
- cross-container movement;
- persistent term UUIDs;
- relocation mixed atomically with width or depth rewrites;
- claims of confidentiality;
- rewriting historical PET-METICA tools.

## 16. Open questions

- Is ordered shape equality explicitly guaranteed by the future representation?
- Should duplicate classes use payload equality defined as equality of
  exponent target shapes after ignoring the local root rank?
- Which non-applied result reason should represent identity or collapsed
  permutations?
- Should external APIs expose only the source-order-vector convention
  fixed by this note?
- Are before and after shape commitments sufficient to protect inverse
  replay against applying the witness to the wrong state?

- Which address effects must be enumerated versus summarized?
- Are shape commitments required for witness replay?
- Which relocation targets are structurally compatible?
- Should `SWAP` be public API or merely syntactic sugar for `PERMUTE`?
- Can relocation participate in shape-native PEG graph edges?
- Does the relocation cost depend on the number of moved terms, cycle count, or
  one atomic rewrite?
- What threat model, if any, makes `SCRAMBLE` useful beyond structural research?

## Current bounded conclusion

The future object-native contract leaves room for an observable relocation
family because containers own ordered visible terms and canonicalization
recomputes positional ranks rather than sorting payloads.

The minimum safe research progression is:

```text
SWAP
    -> explicit transposition semantics

PERMUTE
    -> explicit bijective sibling reordering

SCRAMBLE
    -> secret and unbiased selection of PERMUTE
```

Deterministic relocation semantics, canonical equality, address effects, no-op
behavior, and inverse witnesses must be settled before cryptographic permutation
selection is designed.

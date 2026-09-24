# AIP-2 relation ontology

## Status

Research note for issue #256.

This note is non-normative. It does not change `docs/reference/SPEC.md`, the
runtime object model, public APIs, CLI behavior, serialization, addressing,
operator semantics, or Resolver behavior.

AIP-2 asks what, if anything, must remain in PETRA after arithmetic relation
vocabulary and representation machinery are erased.

The working question is deliberately stricter than the current specification:

> Does abstract PETRA require a distinct relation object, or only recursive
> containment of PETRA forms?

The answer in this note is provisional research classification, not yet a
normative change.

## Starting point: the current model

The current normative grammar is conceptually:

```text
PETRA     ::= Leaf | Container
Container ::= Product(Term+)
Term      ::= Root ^ PETRA
```

The executable model reflects that decomposition directly:

- `Leaf` is the terminal shape;
- `Container` stores non-empty `Term` objects;
- every `Term` stores one positional `Root`;
- every `Term` stores exactly one complete PETRA object in `exponent`;
- equality, hashing, validation, normalization, serialization, addressing and
  operators traverse through `term.exponent`.

This is the current executable contract. AIP-2 does not dispute that fact.
It asks whether every part of that decomposition is intrinsic to the fully
abstract carrier.

## Arithmetic Erasure Test

Erase the following from the abstract description:

- `prime`;
- `integer`;
- `product`;
- `exponent`;
- `factorization`;
- `root` in the arithmetic sense;
- `^`;
- every numerical example and projection.

What remains structurally observable is that a PETRA form is either terminal or
contains one or more PETRA forms, each recursively defined by the same rule.

A neutral candidate carrier is therefore:

```text
Form ::= Terminal | Composite(Collection(Form+))
```

After the AIP-3 result on sibling order, the stronger candidate is:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

This grammar contains no distinct relation symbol. Recursive containment is
encoded by the inductive constructor itself.

The Arithmetic Erasure Test therefore does not establish a need for `^`, an
exponent relation, or a relation node/slot as primitive ontology.

## Recursive containment versus a distinct relation

There are two different claims that must not be conflated:

1. a composite form contains recursive subforms;
2. a distinct relation object connects each component occurrence to one
   recursive target.

The first claim is required by the candidate recursive carrier.

The second is additional structure. It needs independent justification.

In the minimal carrier, the child occurrence already *is* one recursive PETRA
form. No extra edge label is needed to say that it is contained by its parent.
The parent/child relation is derivable from occurrence position in the recursive
construction.

This parallels the result of the level-derivability sub-test: a structural fact
can be real and useful without being independently stored as ontology.

## Wrapper-erasure test

Consider the current structural fragment:

```text
Term(root=R, exponent=X)
```

Erase `Root`, rank, the `Term` wrapper and exponent vocabulary, retaining only
`X` as one child occurrence of its containing composite.

The mapping is:

```text
Container(Term(R0, X0), ..., Term(Rn, Xn))
    ->
Composite({X0, ..., Xn})
```

where braces denote a multiset rather than a set.

### What is preserved

The mapping preserves, as candidate abstract structure:

- terminal versus composite distinction;
- recursive containment;
- multiplicity of structurally equal children;
- recursive depth and levels as derived properties;
- child-shape inventory;
- node/shape structure once representation-only `Term`/`Root` accounting is
  excluded from ontology;
- the ability to distinguish different recursive multisets of subforms.

### What is erased

The mapping erases:

- positional root rank;
- ordered sibling position;
- the `Term` wrapper as a separately named object;
- the `exponent` field name;
- the `^` notation;
- address spelling tied to `Term`/slot vocabulary;
- serialization punctuation tied to the current grammar;
- current witness wording that names terms or exponent slots.

These are operationally real in v2.0.0 but are not, by that fact alone,
abstract ontology.

### What would prove the wrapper necessary

`Term` would need to survive as CORE only if erasing it destroyed some intrinsic
property that cannot be reconstructed from recursive occurrence structure.
Examples would include independently justified per-component identity, relation
kind, orientation, annotation, or arity that belongs to every interpretation.

No such universally required property has yet been established.

Therefore `Term` is currently a **REPRESENTATION candidate**, not established
CORE ontology.

## Relation-arity test

The current model says each `Term` owns exactly one recursive target.

AIP-2 asks whether "exactly one relation target" is itself ontology.

### Exactly one target

After wrapper erasure, this statement becomes tautological rather than a new
axiom: one child occurrence is one PETRA form.

```text
child occurrence = one Form
```

There is no separately existing relation whose cardinality must be constrained
to one.

### Zero targets

A child occurrence with no recursive form would not be an occurrence of `Form`
at all. The role currently played by a terminal target is instead represented
by `Terminal` itself.

Thus an optional/zero relation is unnecessary in the minimal carrier.

### Multiple targets per relation

A relation object owning multiple PETRA targets would introduce another layer
between a composite and its children. The same recursive branching is already
expressible by the composite constructor itself.

Without an independent semantic distinction, this extra n-ary relation layer is
structurally redundant.

### Labeled relation kinds

Different relation labels could be useful in particular interpretations, but
that is precisely why they should not be forced into the maximally abstract
carrier without evidence that every PETRA interpretation requires them.

Candidate classification:

```text
recursive child occurrence   = CORE candidate
relation cardinality object  = not independently justified
relation label/kind           = INTERPRETATION or extension candidate
```

## The `^` symbol

At full abstraction, `^` is not neutral notation.

It has an overwhelmingly conventional mathematical reading as exponentiation.
Retaining it in the abstract grammar would therefore carry interpretation
semantics into a layer whose purpose is to precede interpretation.

The structural fact currently written as:

```text
Root ^ PETRA
```

can be expressed without arithmetic notation as:

```text
one recursive child occurrence
```

or simply by the recursive grammar itself.

Provisional classification:

```text
^ = INTERPRETATION / historical notation
```

This does not make `^` invalid in an arithmetic projection or compatibility
notation. It makes it unsuitable as a primitive symbol of the totally abstract
carrier unless new independent justification is found.

## Root after AIP-3

AIP-3 established strong evidence that sibling sequence position is not
intrinsic abstract identity. Current roots are positional ranks reconstructed
from that sequence.

Therefore AIP-2 does not find a new ontological role for `Root`.

Once order is demoted from ontology, `Root(rank)` remains useful for the current
representation, addressing and serialization system, but there is no evidence
here that it must survive inside abstract form identity.

Provisional classification:

```text
Root / rank = REPRESENTATION candidate
```

## Operator-survival test

The strongest possible objection to wrapper erasure is that current operators
might require the distinct `Term -> exponent` relation slot.

The current implementation does traverse and replace `term.exponent`. That is
implementation evidence, not yet ontological necessity.

AIP-2 therefore restates the structural effects using only recursive
containment.

### SPROUT

Current effect: add one terminal term to a selected container.

Minimal-carrier form:

```text
Composite(M) -> Composite(M + {Terminal})
```

No distinct relation object is required.

### SHED

Current effect: remove one eligible terminal term; if it was the final term,
restore `Leaf`.

Minimal-carrier form:

```text
Composite(M + {Terminal}) -> Composite(M)
```

with singleton collapse:

```text
Composite({Terminal}) -> Terminal
```

when SHED removes the only child occurrence.

Target selection and deterministic tie-breaking remain representation-policy
questions.

### GRAFT

Current implementation targets a latent exponent slot whose target is `Leaf`
and replaces that target by a singleton container containing `Leaf`.

Ignoring current slot vocabulary, the structural effect is:

```text
Terminal occurrence -> Composite({Terminal})
```

inside an existing parent composite.

This operation can therefore be expressed as replacement of one recursive child
occurrence. No separate latent relation object is required to state the shape
change.

The current restriction that a root-level standalone `Leaf` is not itself a
GRAFT slot can be expressed as an eligibility rule on occurrence context:
GRAFT acts on a terminal occurrence contained by another form, not necessarily
on the root form itself. That contextual restriction does not require a stored
relation node.

### PRUNE

Current implementation is inverse-like: an eligible nested singleton container
whose sole term targets `Leaf` collapses back to the latent leaf target.

Minimal-carrier form:

```text
Composite({Terminal}) occurrence -> Terminal
```

subject to the same parent/eligibility conditions.

Again, the effect is definable directly on recursive occurrence structure.

### Operator result

All four local shape effects survive wrapper erasure at the level tested here.

What does *not* automatically survive unchanged is the current target language:

- numeric term addresses;
- slot addresses ending in `^`;
- rank-based ownership;
- first/last/preorder defaults;
- witness spelling.

Those are representation contracts and require redesign if the ontology is
later promoted. Their existence does not prove a distinct relation primitive.

## Latent slot test

The current specification gives special status to a latent exponent slot even
when its target is `Leaf`.

AIP-2 asks whether that slot contains structural information beyond the terminal
child itself.

For a current term with exponent `Leaf`:

```text
Term(R, Leaf)
```

the proposed abstract representation is simply:

```text
Terminal
```

For the materialized one-level-deeper case:

```text
Term(R, Container(Term(R0, Leaf)))
```

the abstract representation is:

```text
Composite({Terminal})
```

The two states remain distinct without an explicit latent slot:

```text
Terminal != Composite({Terminal})
```

Therefore the slot is not required merely to preserve the distinction that
GRAFT and PRUNE manipulate.

The distinction is already encoded by recursive shape.

## Equality under wrapper erasure

A candidate fully abstract equality after AIP-3 and AIP-2 is recursive multiset
equality:

```text
Terminal == Terminal

Composite(M) == Composite(N)
    iff M and N are equal multisets of recursively equal Forms
```

This equality requires neither rank nor `Term` nor relation labels.

A formal isomorphism claim between this carrier and a quotient of the current
runtime still requires a dedicated proof/prototype. This note therefore does
not claim the isomorphism as established fact.

The natural candidate quotient forgets recursively:

1. sibling permutations;
2. positional `Root` ranks;
3. the `Term` wrapper;
4. exponent/relation naming.

Multiplicity must remain preserved.

## Representation audit

The current runtime has several features that make the relation appear more
substantial than it may be ontologically.

### Addresses

Current addresses select terms and may append `^` to select a slot. This is a
coordinate system over the current representation.

If the abstract carrier contains only recursive occurrences, a future
representation can still assign deterministic coordinates to occurrences.
The coordinate need not be part of abstract identity.

### Serialization

Current text serializes `rN^...`. Removing `Root`, `Term` and `^` from ontology
would require a different canonical serialization, but serialization is a
representation problem. A change requirement does not itself establish an
ontological requirement.

### Validation and normalization

Current validation ensures rank/position consistency and recursively validates
`term.exponent`. A minimal carrier would instead validate terminal/composite
construction and multiplicity-preserving recursive children.

### Witnesses

Current witnesses report term and slot addresses. A future abstract witness can
still identify a changed occurrence through representation-level coordinates.

### Resolver

Resolver enumerates addresses and operators over the current model. Its search
graph is therefore representation-dependent today. As with the AIP-3 quotient,
a future abstract resolver would operate on the promoted carrier or canonical
representatives of its equivalence classes.

No Resolver behavior is changed by this research note.

## Counterexample criteria

The hypothesis "recursive containment is sufficient" should be rejected if a
representation-independent counterexample is found.

A valid counterexample would need to establish at least one of the following:

1. two forms with identical recursive containment/multiplicity but different
   intrinsic PETRA identity solely because of a relation object;
2. an intrinsic operator whose outcome cannot be defined from recursive
   occurrence structure without relation labels or relation identity;
3. an invariant admitted to CORE that distinguishes relation metadata after
   roots, order, addresses and arithmetic interpretation are erased;
4. an interpretation-independent reason every component must possess a
   separately identifiable edge/relation object;
5. an intrinsic need for multiple relation kinds not reducible to recursive
   composition itself.

The following do **not** count as counterexamples by themselves:

- current `^` syntax;
- current `ResolvedSlot` type;
- current address spelling;
- current `Term` dataclass;
- current root ranks;
- default traversal order;
- arithmetic projection;
- serializer/parser compatibility requirements.

Those prove implementation dependence, not ontology.

## Provisional AIP-2 classification

The evidence audited here supports the following research classification:

```text
Terminal / termination              = CORE candidate
recursive containment               = CORE candidate
child multiplicity                  = CORE candidate (subject to AIP-1)
level / depth                       = DERIVED CORE PROPERTY
sibling order                       = REPRESENTATION / interpretation-dependent
Root / positional rank              = REPRESENTATION
Term wrapper                        = REPRESENTATION candidate
^                                   = INTERPRETATION / historical notation
"exponent relation" vocabulary      = INTERPRETATION
explicit latent relation slot       = not independently justified
relation labels / kinds             = INTERPRETATION or extension candidate
```

The important negative result is:

> No audited structural requirement currently forces a distinct relation
> primitive in addition to recursive containment.

The important positive candidate is:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

However, `Multiset(Form+)` still bundles an AIP-1 assumption: that the abstract
composition operator itself is genuinely intrinsic. AIP-2 should therefore not
promote this grammar to SPEC before AIP-1 is completed.

## AIP-2 conclusion

Within the scope audited here, the current `Root ^ PETRA` decomposition appears
to combine three layers:

```text
CORE candidate:
    one recursive PETRA occurrence contained by another form

REPRESENTATION:
    Term wrapper
    positional Root/rank
    addressable slot machinery

INTERPRETATION / historical vocabulary:
    exponent
    ^
```

The strongest current AIP-2 hypothesis is therefore:

> PETRA does not need an independently existing relation primitive at the
> totally abstract layer. Recursive containment is sufficient to express the
> tested structure and local rewrite effects.

This remains a hypothesis until the wrapper-erasure mapping is formally tested
as a quotient/isomorphism candidate over the current carrier and until AIP-1
settles the composition ontology.

## Recommended next test

Before closing AIP-2, build a small research-only prototype that maps current
canonical shapes to the wrapper-erased recursive carrier and checks:

1. rank and `Term` erasure preserves multiplicity and recursive form;
2. AIP-3 permutation-equivalent states map to the same abstract form;
3. GRAFT/PRUNE structural effects commute with the erasure map on a bounded
   corpus;
4. SPROUT/SHED structural effects commute modulo sibling order;
5. no accidental collisions occur beyond those intentionally induced by
   order/rank/wrapper erasure.

That prototype would provide executable evidence for the central AIP-2 claim
without changing production semantics.

# AIP-2 recursive containment prototype

## Status

Research-only executable validation for issue #261 under AIP-2 issue #256.

This note does not change the canonical PETRA specification, runtime object
model, APIs, CLI, serialization, addressing, operator semantics, or Resolver.

The purpose is narrower: strengthen the hypothesis that the totally abstract
PETRA layer needs recursive containment, but not a distinct relation primitive.

## Hypothesis under test

The current runtime represents one recursive occurrence through:

```text
Term(root=Root(rank), exponent=PETRA)
```

The candidate abstract carrier instead keeps only recursive form:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

At this layer:

- `Root` and positional rank are representation;
- `Term` is not assumed to be ontology;
- `exponent` and `^` are interpretation/historical vocabulary;
- sibling order is not intrinsic under the AIP-3 hypothesis;
- multiplicity is preserved;
- recursion is explicit through containment itself.

The executable question is therefore:

> If Root, Term, exponent naming, `^`, and sibling order are erased, can the
> currently identified structural effects still be represented without loss
> on a bounded corpus?

A positive result strengthens AIP-2. It does not establish a final ontology.
AIP-1 composition ontology remains open.

## Prototype

The probe is:

```text
tools/research/aip2_recursive_containment_probe.py
```

It defines two research-only views.

### Ordered wrapper erasure

`erase_ordered()` maps the current model to neutral recursive containment while
retaining child sequence temporarily as a coordinate harness:

```text
Leaf
  -> Terminal

Container(Term(r0, X0), Term(r1, X1), ...)
  -> Composite(X0, X1, ...)
```

The retained sequence is not treated as ontology. It exists only so current
positional addresses can identify the same occurrence during the operator
commutation checks.

### Abstract key

`abstract_key()` recursively removes sibling order by sorting only the
structural keys used to materialize a multiset deterministically:

```text
Terminal

Composite(multiset(child abstract keys))
```

The sort operation is representation-only; the intended abstract object is a
multiset, not a sequence.

## Checks

### 1. Wrapper erasure

The probe confirms that a representative current structure can be mapped to a
recursive form containing no Root spelling, `^`, or `exponent` vocabulary.

This is a constructive Arithmetic Erasure Test at the executable level.

### 2. AIP-3 compatibility

Two current shapes that differ only by sibling permutation remain unequal in the
v2.0.0 runtime but map to the same AIP-2 abstract key.

This checks that relation-wrapper erasure is compatible with the previously
studied sibling-permutation quotient.

### 3. Multiplicity preservation

One, two, and three equal terminal child occurrences must remain distinct
abstract forms.

The candidate carrier is therefore multiset-like rather than set-like.

### 4. Operator commutation

The probe checks the four current structural operators against relation-free
recursive transformations.

The current positional address is used only to identify the tested occurrence.
The expected result is computed on the wrapper-erased recursive form.

#### SPROUT

Abstract effect:

```text
Terminal -> Composite({Terminal})
```

when applied to the root terminal, or:

```text
Composite(M) -> Composite(M + {Terminal})
```

for a selected composite occurrence.

#### SHED

Abstract effect:

```text
Composite(M + {Terminal}) -> Composite(M)
```

with terminal restoration when the removed child was the only occurrence:

```text
Composite({Terminal}) -> Terminal
```

#### GRAFT

The current runtime addresses a latent `^` slot. The relation-free structural
effect is tested directly as:

```text
Terminal occurrence -> Composite({Terminal})
```

Thus the existence of the current slot address is not assumed to imply an
ontological relation object.

#### PRUNE

For a nested singleton composite whose sole child is terminal:

```text
Composite({Terminal}) occurrence -> Terminal
```

The current leaf-term address is used as a representation coordinate; the
expected abstract rewrite acts on its containing singleton composite.

### 5. Bounded collision search

The corpus contains one representative per abstract form up to:

```text
max_depth = 2
max_width = 3
```

Root-level ordered variants are materialized and erased. The number of abstract
classes must remain equal to the representative count.

A failure would indicate a collision beyond the intended removal of sibling
order and relation-wrapper representation within this bounded corpus.

## What a PASS would support

A complete PASS supports the following research statement:

> Over the tested bounded corpus, Root/Term/exponent-relation representation can
> be erased while preserving recursive multiplicity structure and reproducing
> the local structural effects of SPROUT, SHED, GRAFT, and PRUNE modulo sibling
> order.

That is stronger than a purely verbal argument because the candidate carrier is
made executable and compared against current behavior.

## What a PASS would not prove

A PASS does **not** prove that:

- AIP-2 is absolutely or permanently settled;
- the candidate carrier is the final PETRA ontology;
- the bounded corpus constitutes an unbounded mathematical proof;
- composition itself is intrinsic; that remains AIP-1;
- current addresses, serialization, defaults, or witnesses can be removed
  without redesign;
- all future PETRA interpretations must use only this structure.

The appropriate interpretation is therefore:

```text
AIP-2 hypothesis:
    strengthened by executable evidence
```

not:

```text
AIP-2:
    closed forever
```

## Counterexample policy

The hypothesis should be weakened or rejected if a representation-independent
counterexample is found in which two forms with identical recursive
containment/multiplicity require different intrinsic PETRA identity or behavior
solely because of an independently meaningful relation object.

Current implementation facts such as `ResolvedSlot`, `^` syntax, rank-bearing
addresses, or the `Term` dataclass do not constitute such a counterexample by
themselves.

## Expected invocation

From the repository virtual environment:

```bash
PYTHONPATH=src python tools/research/aip2_recursive_containment_probe.py
```

Then run the repository research-document gates used for recent AIP work:

```bash
make docs-check
pytest -q tests/test_report_contracts.py
```

The exact probe counts are intentionally recorded from execution rather than
predicted in this note.

## Research classification if the probe passes

Subject to the bounded scope and AIP-1 caveat:

```text
Terminal / termination          = CORE candidate
recursive containment           = CORE candidate
child multiplicity              = CORE candidate, pending AIP-1
level / depth                   = DERIVED CORE PROPERTY
sibling order                   = REPRESENTATION / interpretation-dependent
Root / positional rank          = REPRESENTATION
Term wrapper                    = REPRESENTATION candidate
^                               = INTERPRETATION / historical notation
exponent-relation vocabulary    = INTERPRETATION
explicit latent relation slot   = not independently justified
```

The key question remains open to future counterevidence, but the burden shifts:
a distinct relation primitive would need an intrinsic role that cannot be
reconstructed from recursive containment itself.

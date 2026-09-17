# AIP-1 Set vs Multiset executable prototype

## Status

Research note under issues #263 and #266, following the conceptual multiplicity analysis in #264.

This note is non-normative. It does not change SPEC, runtime semantics, APIs, CLI behavior, serialization, addressing, operators, or Resolver behavior.

## Question

AIP-1 asks whether duplicate child count is part of abstract PETRA composition.

The executable comparison is between:

```text
Multiset model:
Form ::= Terminal | Composite(Multiset(Form+))

Set model:
Form ::= Terminal | Composite(Set(Form+))
```

Both ignore sibling order. They differ only when recursively equal children repeat.

## Probe

The research-only executable probe is:

```text
tools/research/aip1_set_vs_multiset_probe.py
```

It uses current valid PETRA shapes as source material and computes two independent abstraction keys:

- `multiset_key`: recursively erases sibling order while preserving duplicate counts;
- `set_key`: recursively erases sibling order and duplicate equal children.

No production representation or equality function is changed.

## Required witnesses

### Duplicate-count witness

```text
Composite({Terminal})
Composite({Terminal, Terminal})
Composite({Terminal, Terminal, Terminal})
```

The multiset abstraction must keep all three distinct.
The set abstraction must collapse all three.

### SPROUT witness

Starting from:

```text
Composite({Terminal})
```

one root SPROUT produces the current-model equivalent of:

```text
Composite({Terminal, Terminal})
```

Expected comparison:

```text
multiset(before) != multiset(after)
set(before)      == set(after)
```

If observed, set semantics makes a successful width-changing rewrite invisible.

### SHED witness

Starting from two equal terminal children, explicit SHED removes one occurrence.

Expected comparison:

```text
multiset(before) != multiset(after)
set(before)      == set(after)
```

Again, set semantics loses an accepted structural distinction.

### GRAFT / PRUNE control witness

The singleton depth change

```text
Terminal <-> Composite({Terminal})
```

must remain visible under both abstractions.

This control matters because it shows the failure of set semantics is not a blanket inability to observe rewrites. It is specifically tied to duplicate-count erasure.

## Bounded class search

The probe also builds one representative per bounded multiset form at:

```text
max_depth = 2
max_width = 3
```

and enumerates root-level sibling permutations.

Expected properties:

1. sibling permutations collapse under both abstractions;
2. multiset class count equals the representative count;
3. set class count is strictly smaller;
4. the difference counts bounded composition distinctions lost only because duplicate child multiplicity is erased.

The exact observed counts are intentionally reported by execution rather than asserted here before running the probe.

## Interpretation

A passing probe supports the following research classification:

```text
child collection                = CORE candidate
child multiplicity              = CORE candidate, strengthened by executable evidence
persistent occurrence identity  = not established CORE
sibling order                   = not CORE
positional rank                 = REPRESENTATION
```

The key result would be negative evidence against `Set(Form+)` as a sufficient carrier: it cannot faithfully represent multiplicity-sensitive width changes already expressible without arithmetic interpretation.

## Limits

A passing bounded probe is not a proof of final PETRA ontology.

It does not settle:

- empty composition;
- whether `Terminal` and `Composite(empty)` should coincide;
- whether unary composites collapse to their child;
- grouping, associativity, or flattening;
- whether composition requires an algebraic operator beyond recursive constructor syntax;
- all unbounded behaviors.

Those remain separate AIP-1 questions under #263.

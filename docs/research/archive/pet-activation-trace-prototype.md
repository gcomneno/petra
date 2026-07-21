# PET Activation Trace Prototype

## Status

Archived research experiment. Not promoted to PET-Base, PET/PEG 2.0
foundations, stable CLI behavior, routing policy, or canonical terminology.

The implementation and its tests remain recorded in the historical commits:

- `035ad4a2dc4f55d243fce0956061263d1887481b` — initial activation-trace prototype
- `ff080df3c5f80c381946c31884a14a29b427fb95` — activation-profile comparison

The source files from those commits were intentionally not integrated into
`main`.

## Research question explored

The prototype asked whether a PET object could be viewed as a sequence of
active structural frontiers across increasing graph depth.

It represented:

- a seed frontier;
- successive reachable frontiers;
- an optional target;
- a bounded traversal depth;
- a terminal frontier;
- a replayable trace certificate.

When connected to a PET object, it also summarized each frontier by:

- active object count;
- atomic object count;
- composite object count.

A comparison mode grouped integers by the resulting
`active/atomic/composite` profile.

## What the prototype established

The experiment demonstrated that:

1. PET object addresses can be projected into a deterministic parent-to-child
   graph.
2. Bounded breadth-first frontiers can be emitted and replay-verified.
3. Frontier members can retain PET object metadata such as address, value,
   role, kind, prime label, and children.
4. Different integers can be compared by compact structural frontier
   profiles.
5. The implementation remained explicitly research-only and did not alter
   PET core behavior.

The historical branch contained 748 lines of prototype code and 421 lines of
focused tests. Its observable contract covered depth bounds, target reach,
address canonicalization, trace verification, PET object details, summary
output, JSON output, and profile comparison.

## Why it was not promoted

The prototype was technically coherent, but promotion was not justified.

### Terminology risk

The terms `activation`, `propagation`, and `causal_depth` suggest stronger
physical or causal semantics than the implementation provides.

Operationally, the prototype performs bounded traversal over structural graph
levels. No claim about light, physical propagation, object motion, or a new
causal PET semantics was established.

### Existing semantic coverage

Current PET documentation and APIs already define structural height and
object-native structural metrics.

The prototype's traversal depth therefore overlaps substantially with
existing height semantics, while its frontier composition profile has not yet
been shown to answer a distinct project-level question.

### Missing discriminating hypothesis

The `active/atomic/composite` profile is an original experimental descriptor,
but the historical work did not establish that it:

- distinguishes relevant PET families better than existing metrics;
- predicts operator behavior;
- improves routing or recognition;
- exposes an invariant unavailable from current structural descriptors.

Without such a hypothesis, integrating the implementation would preserve a
solution before establishing the problem it solves.

## Relationship to current PET architecture

This prototype traverses levels inside one PET-derived structural graph.

That must remain distinct from current PET/PEG graph and trace work concerning
operator transformations, route histories, and certificates between PET
states. Similar graph vocabulary does not make these layers equivalent.

It also must not redefine the public `height(...)` API or introduce a generic
causal interpretation of recursive exponent depth.

## Archival decision

The experiment is preserved as historical research documentation, while its
1,169 lines of code and tests remain outside `main`.

This choice:

- preserves provenance and the useful observations;
- avoids accidental promotion through executable tooling;
- prevents duplicate structural-depth terminology;
- leaves a precise reopening condition.

## Reopening condition

Reopen this line only with a bounded, falsifiable question showing that the
frontier-composition profile adds information beyond existing PET metrics.

A future pass should define in advance:

1. the target phenomenon;
2. the baseline metrics used for comparison;
3. the bounded dataset or PET family;
4. the success and failure criteria;
5. neutral terminology such as `structural frontier profile`;
6. the intended stability layer if the result is positive.

Until then, this remains an archived experiment rather than an active PET
research route.

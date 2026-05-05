# PET Backbone Landmark Projection

## Motivation

The current PET-shadow line has produced useful diagnostic tools, but it has
not yet produced a decisive reduction operator.

The existing projection layers are:

- `Π_shape`: local visible segment projection;
- `Ω_shape`: positional overlap projection;
- route correlation: comparison against decimal rigidity and full PET signature
  cost.

These tools can classify visible shadow structure, but they still operate mostly
on contiguous visible digit segments.

The next hypothesis is different:

> The PET family relation may live in a sparse backbone support, not in a
> contiguous visible segment.

In other words, a PET shape may not be explained by reading one continuous slice
of the backbone.  It may instead depend on a sparse constellation of backbone
landmarks.

## PE-Tree viewpoint

In the PE-Tree picture, the backbone is the generative hub.

It behaves like an ancestor line from which PET-shape branches originate.  From
this viewpoint, the backbone is not only a linear string to be sliced into
contiguous pieces.  It is also a source of branching landmarks.

The current concern is that contiguous segment search may be too restrictive.

A branch may be controlled by landmarks such as:

    b_2, b_5, b_11

rather than by a continuous interval such as:

    b_2, b_3, b_4, b_5

This suggests that the correct PET-native object may be a sparse support over
the backbone.

## Current implementation note

The current backbone implementation is prefix-based.

In `tools/core/pet_local_probe_proposal.py`, the selected backbone is built as:

    selected_backbone_primes = first_primes(selected_backbone_order)
    selected_backbone_generator = prod(selected_backbone_primes)

So the current model is:

    B_k = product(first_primes(k))

This is a contiguous prefix of the prime backbone.

The sparse-support hypothesis must therefore be careful.  A naive sparse subset
of prime values may collapse under PET canonicalization.  For example, different
square-free products with the same number of prime factors can share the same
PET shape and canonical generator.

Therefore, a PET-native backbone landmark should probably not be defined only as
a raw selected prime value.

More plausible PET-native landmark types include:

- backbone order candidates;
- canonical generator families;
- shape paths;
- primitive shape moves (`NEW`, `DROP`, `INC`, `DEC`);
- nodes in a local `shape_closure`;
- PE-Tree branching landmarks.

This refines the hypothesis:

> `Σ_backbone(N)` should search for sparse PET-native shape/backbone landmarks,
> not merely sparse subsets of prime values.

## Core hypothesis

The core hypothesis is:

> A large opaque integer `N` may project to a sparse set of PET-backbone
> landmarks.  This support may identify a PET-shadow family more directly than
> decimal morphology or contiguous segment projections.

This support is not a factorization of `N`.

It is not `PET(N)`.

It is not the true generator of `N`.

It is a shadow support: a candidate sparse explanation of the visible PET-shadow
field.

## Proposed operator: Σ_backbone

The proposed projection operator is:

    Σ_backbone(N)

Informal definition:

    Σ_backbone(N) returns a sparse set of PET-backbone landmarks that best
    explains the stable PET-shadow generator field of N.

A possible output shape is:

    {
      "N": "...",
      "support_status": "found|weak|none",
      "backbone_landmarks": [...],
      "support_generators": [...],
      "support_confidence": "...",
      "evidence": {...},
      "claim": "shadow backbone support only; not PET(N)"
    }

The important point is that the returned object is a support, not a number.

## Relation to Γ_shadow

A second derived operator may be useful:

    Γ_shadow(N) = closure(Σ_backbone(N))

Informal meaning:

    Γ_shadow(N) is the PET-shadow family generator suggested by the sparse
    backbone support.

This is still not the true PET generator of `N`.

The relation is:

    N
      -> PET-shadow field
      -> sparse backbone support
      -> shadow family generator

or symbolically:

    N --Σ_backbone--> support(backbone) --Γ_shadow--> family generator

## Why this differs from Π_shape and Ω_shape

`Π_shape` asks:

    Which visible segments locally resonate with known PET generators?

`Ω_shape` asks:

    Do those local projections overlap coherently across digit positions?

`Σ_backbone` asks:

    Which sparse backbone landmarks could explain the stable generator field?

This is a more PET-native question.

It moves away from decimal morphology and toward generative support.

## Why contiguous segments may fail

Contiguous visible segments assume that the relevant structure is local in the
visible representation.

That may be false.

The relevant PET family may depend on:

- sparse landmarks;
- repeated branching points;
- non-adjacent backbone nodes;
- multi-scale generator recurrence;
- a constellation of support points rather than a single interval.

Therefore, a number may look diffuse under segment projection while still having
a sparse backbone explanation.

This is the main reason to study `Σ_backbone`.

## Evidence sources

A future implementation should not brute-force arbitrary subsets.

The support must be constrained by evidence already produced by PET-shadow
tools.

Potential evidence sources:

### 1. Stable shadow generators

Generators that appear repeatedly across `Π_shape` scales may suggest backbone
landmarks.

Example evidence:

    dominant generator = 12
    stable across sqrt-digits/log2-digits
    high dominant ratio

### 2. Positional overlap coherence

`Ω_shape` can identify whether local generator evidence is coherent,
dominant-but-noisy, mixed, or diffuse.

Strong evidence:

    coherent-single-generator-overlap

Moderate evidence:

    coherent-dominant-overlap
    dominant-diffuse-overlap

Weak evidence:

    mixed-overlap-field

Negative evidence:

    diffuse-overlap-field
    no-visible-overlap

### 3. Target-basis robustness

A candidate support is stronger if it does not disappear under small changes to
the target generator basis.

However, single-generator resonance can be target-sensitive.  This must be
reported, not hidden.

### 4. Multi-scale recurrence

A landmark candidate is stronger if related generator evidence appears across
multiple scale rules.

The exact winning scale is less important than recurrence.

### 5. PE-Tree closure behavior

A future PET-native test should ask whether the proposed landmarks induce a
stable family under local PE-Tree expansion.

This part is still open.

## Anti-goals

`Σ_backbone` must not become brute force subset search.

Do not do:

    for subset in all_backbone_subsets:
        test(subset)

That explodes combinatorially and risks becoming meaningless.

`Σ_backbone` must also not claim:

- factorization;
- divisibility;
- the true `PET(N)`;
- the true generator of `N`;
- mathematical equivalence between `N` and the support.

The claim is only:

    shadow backbone support only; not PET(N)

## Initial qualitative examples

These are conceptual examples only.

### Periodic 90 field

Input:

    9090909090909090909090909

Existing evidence:

    Π_shape: has-single-generator-scale
    Ω_shape: coherent-single-generator-overlap
    dominant position generator: 12

Possible reading:

    Σ_backbone(N): strong support around generator 12
    Γ_shadow(N): family generator 12

This does not mean that 12 is the true generator of `N`.

### Periodic 12 field

Input:

    1212121212121212121212121

Existing evidence:

    Π_shape: has-strong-scale
    Ω_shape: dominant-diffuse-overlap
    dominant position generator: 30

Possible reading:

    Σ_backbone(N): noisy but strong support around generator 30
    Γ_shadow(N): weak or noisy family generator 30

### Digit-mixed opaque field

Input:

    1234567891234567891234567

Existing evidence:

    Π_shape: diffuse-all-scales
    Ω_shape: diffuse-overlap-field

Possible reading:

    Σ_backbone(N): none
    Γ_shadow(N): none

### Decimal-rigid 9/0 field

Input:

    9999999999000000000119

Existing evidence:

    Π_shape: has-strong-scale
    Ω_shape: mixed-overlap-field
    dominant position generator: 60

Possible reading:

    Σ_backbone(N): weak or partial support around generator 60
    Γ_shadow(N): weak family generator 60

## Acceptance criteria for future tooling

A future `pet_backbone_landmark_projection_study.py` should initially be judged
by these criteria:

1. It must return `none` for strongly diffuse fields unless there is clear
   generator evidence.
2. It must distinguish strong, weak, and absent support.
3. It must report the evidence that selected each landmark.
4. It must avoid exhaustive subset search.
5. It must keep the claim limited to shadow support.
6. It must expose target-basis sensitivity.
7. It must be testable on the existing PET-shadow sample set.

## Open questions

- What exactly is a backbone landmark in the current PET implementation?
- Should landmarks be represented as generators, primorial positions, PE-Tree
  nodes, or another PET-native object?
- What closure operation should define `Γ_shadow` from `Σ_backbone`?
- Can sparse support explain cases where `Π_shape` is diffuse but hidden
  structure still exists?
- Can sparse support guide a cheaper route, or is it only diagnostic?
- How can we constrain the support search without smuggling in classical
  arithmetic?

## Current status

This is a research hypothesis.

It is more PET-native than decimal morphology, but it is not yet implemented.

The next concrete step is to inspect the current code and identify what object
already represents the PET backbone most directly.

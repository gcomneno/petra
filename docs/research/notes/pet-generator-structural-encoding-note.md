# PET generator as canonical structural encoding (bounded note)

## Status

Empirical bounded note.
This is evidence, not a proof.

## Objects

We distinguish three different objects:

- full PET shape: the full rooted recursive structure
- minimal generator: the smallest integer with that PET shape
- branch profile: the levelwise branching summary

The strong rule appears to live on full PET shape, not on branch profile alone.

## Candidate structural encoding

Let `G(T)` denote the minimal generator of a PET shape `T`.

Base case:

- a leaf-shape has code `1`

Recursive step:

- if `T` has child-shapes `T1, ..., Tk`
- let `c_i = G(T_i)`
- sort child-codes in non-increasing order
- then

`G(T) = product_i p_i ^ c_i`

where `p_i` is the `i`-th prime.

Operationally: larger child-codes are assigned to smaller primes.

## Candidate structural decoding

Given a minimal generator

`n = product_i p_i ^ a_i`

decode it recursively as follows:

- each exponent `a_i = 1` corresponds to a leaf child
- each exponent `a_i > 1` is decoded as the minimal generator of a child-shape
- recurse until all exponents are `1`

This suggests that minimal generators are not just representatives of shape classes, but canonical structural encodings.

This decoding claim is intended for minimal generators, not for arbitrary integers in the same PET shape class.

## Bounded evidence

### Encode check

On unique observed PET shapes from the scan up to `1,000,000`:

- unique shapes checked: `78`
- encode mismatches: `0`

### Decode check

On the same unique observed PET shapes:

- decode mismatches: `0`

### Branch-profile projection

For all scanned integers in `2..1,000,000`:

- checked records: `999,999`
- mismatches: `0`

Observed rule:

- the branch profile of a node is the shifted levelwise sum of the branch profiles of its children

Therefore branch profile is a lossy projection of full PET shape.

## Consequence

Distinct full PET shapes can share the same branch profile while having different minimal generators.

So branch profile is useful for exploration, but it is not a complete structural invariant.

## Small collision examples

### Branch profile `[2,2]`

- generator `36`  -> child-codes `[2,2]`
- generator `192` -> child-codes `[6,1]`

### Branch profile `[3,3,1]`

- generator `3600`   -> child-codes `[4,2,2]`
- generator `25920`  -> child-codes `[6,4,1]`
- generator `184320` -> child-codes `[12,2,1]`

These examples show that the same branch-profile can arise from different recursive decompositions of child-shapes.

## Interpretation

The more faithful local structural state is the multiset of child generators, not branch profile alone.

This suggests the following picture:

- full PET shape is the primary object
- minimal generator is its canonical arithmetic encoding
- branch profile is an additive, lossy projection

## Open points

- prove global minimality of the recursive encoding
- characterize when different child-shape decompositions collapse to the same branch profile
- decide whether this should remain a research note or become a user-facing analytical capability

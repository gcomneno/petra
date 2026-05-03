# PET shape stencil probe notes

Status: experimental note.

This note records the current interpretation of the PET shape overlap and stencil-transfer helpers.

## Tools

### tools/shape_overlap.py

Compares two PET shapes and reports:

- structural distance
- overlap ratio from the left side
- overlap ratio from the right side
- common shape
- left residual
- right residual

This is a PET shape comparison tool. It does not factor numbers.

### tools/stencil_lens_probe.py

Uses flat canonical lenses as PET stencils.

For a source shape, it tests candidate flat lenses:

- one-leaf
- two-leaf
- three-leaf
- four-leaf
- ...

For each candidate it reports:

- target coverage
- stencil usage
- structural distance
- role

The best proper lens is the largest fully covered non-identical flat lens with maximal stencil usage.

This selects the shape of the next possible PET cut, not the arithmetic value of a factor.

## Core observation

Raw shape overlap does not identify value-level factors.

Example:

- 35, 55, and 77 have the same two-leaf PET shape.
- 385, 455, 715, and 1001 have the same three-leaf PET shape.

So PET shape alone sees structural class, not factor identity.

This is expected and useful.

## Stencil-transfer interpretation

For a three-leaf source such as 385:

- one-leaf lens uses too little of the source stencil
- two-leaf lens is the best proper lens
- three-leaf lens is identical
- four-leaf lens overshoots

Observed pattern:

- 55 recommends one-leaf
- 385 recommends two-leaf
- 5005 recommends three-leaf

Candidate interpretation:

A k-leaf flat source naturally recommends a k-1 leaf proper lens.

This does not identify which factor or subproduct to peel. It suggests the structural form of the next lens.

## Non-flat shapes

Some shapes are not flat.

Examples:

- 49 and 121 are power-like / deep one-branch shapes.
- 45 and 75 have non-flat depth with multiple root branches.
- 225 has two deeper root branches.

For these cases, the probe reports:

- original source size
- original source height
- flattening steps
- flattening recommended yes/no

The flattening rule is based only on PET-visible shape depth:

flattening_steps = max(0, source_height - 2)

This avoids using known arithmetic exponents.

## Flatten projection

The --flatten option projects each root branch to a flat leaf.

This separates two views:

### Original view

Uses the full PET shape including depth.

### Flattened view

Ignores internal branch depth and keeps only root-level branch count.

Example:

49 without flatten:

- source height = 3
- flattening recommended = yes
- recommended lens = one-leaf

49 with flatten:

- source becomes one-leaf
- no proper flat lens remains

225 without flatten:

- recommended lens = two-leaf

225 with flatten:

- source becomes two-leaf
- recommended lens = one-leaf

Interpretation:

Flattening is a second PET view. It does not replace the original probe.

## Structural mass is not prime factor count

PET structural mass is not the same as classical prime factor count.

A small arithmetic factor may be real, but structurally non-driving.

Example:

- Classic view: 3027009081 = 3 * 1009 * 1000003
- PET lens view: the dominant structural cut is two-leaf
- Operational meaning: the tiny factor 3 should be handled by cheap low-backbone peeling, not by the main stencil lens

In short:

Non tutte le briciole meritano la spada laser.

## What this gives us

The current stencil probe cannot find factors.

It can suggest the structural type of the next cut.

This is useful because it changes the question from:

Which number divides N?

to:

Which PET lens shape should be tried next?

## Current limitations

The probe currently tests only flat canonical lenses.

It does not yet test deeper canonical lenses such as:

- chain-2
- chain-3
- one-deep-plus-one-leaf
- two-deep-branches

These may be needed for better non-flat lens selection.

## Current claim

PET shape stencil probing is diagnostic only.

It does not factor N.

It does not prove primality.

It selects candidate structural lens forms for future PET-local probing.

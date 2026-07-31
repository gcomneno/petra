# PET first-principles worked examples

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


This document gives small worked examples for the PET seed idea.

PET observes positive integers as recursive prime-exponent structures.

The examples below are not algorithms for discovering factorization.

They assume that the prime-exponent structure is already known, then show how
that structure is represented recursively as PET objects.

## Notation

`PET(n)` means the canonical PET object for the positive integer `n`, once the
prime-exponent structure of `n` is known.

The recursive rule is:

    PET(n) = product of p^PET(e)

for every prime-power component:

    p^e

in the classical factorization of `n`.

The leaf object is:

    PET(1) = 1

This keeps recursion finite.

## Construction boundary

These examples do not remove factorization cost.

If `n` is given as an opaque integer, constructing `PET(n)` requires knowing or
recovering the prime-exponent structure of `n`.

PET is being used here as a structural lens, not as a magic parser for large
integers.

## Example 1: n = 1

Classical value:

    1

Classical factorization:

    empty product

PET object:

    PET(1) = 1

Structural reading:

`1` is the leaf PET object.

It terminates recursion.

What PET makes visible:

- the base object of the representation
- the stopping point for exponent recursion

What PET does not make easier:

- there is no arithmetic shortcut here
- this is a modeling convention, not a primality claim

## Example 2: n = 2

Classical factorization:

    2 = 2^1

PET object:

    PET(2) = 2^PET(1)
           = 2^1

Structural reading:

The prime root is `2`.

Its exponent object is the leaf PET object.

What PET makes visible:

- a prime is a one-root object with leaf exponent
- `2` is structurally shallow

What PET does not make easier:

- detecting that `2` is prime is still outside this representation step

## Example 3: n = 4

Classical factorization:

    4 = 2^2

PET object:

    PET(4) = 2^PET(2)
           = 2^(2^1)

Structural reading:

The numeric exponent `2` is itself represented as a PET object.

Instead of reading only:

    2 squared

PET reads:

    root 2 whose exponent is the PET object for 2

What PET makes visible:

- exponent recursion begins immediately
- `4` has more vertical structure than `2`

What PET does not make easier:

- the value is still 4 after collapse
- PET does not make `4 = 2^2` disappear as input knowledge

## Example 4: n = 8

Classical factorization:

    8 = 2^3

PET object:

    PET(8) = 2^PET(3)
           = 2^(3^1)

Structural reading:

`8` and `4` share the same root `2`, but their exponent objects differ:

    PET(4) uses PET(2)
    PET(8) uses PET(3)

What PET makes visible:

- same base root
- different exponent-object identity
- exponent structure can distinguish powers of the same prime

What PET does not make easier:

- PET does not automatically reveal that 8 is a power of 2 from opaque digits

## Example 5: n = 12

Classical factorization:

    12 = 2^2 * 3^1

PET object:

    PET(12) = 2^PET(2) * 3^PET(1)
            = 2^(2^1) * 3^1

Structural reading:

`12` has a two-root baseline:

    {2, 3}

The root `2` has a recursive exponent object.

The root `3` has a leaf exponent.

What PET makes visible:

- support topology: roots 2 and 3
- asymmetric exponent depth between roots
- a difference between baseline breadth and exponent height

What PET does not make easier:

- PET does not avoid knowing that 12 has roots 2 and 3

## Example 6: n = 16

Classical factorization:

    16 = 2^4

PET object:

    PET(16) = 2^PET(4)
            = 2^(2^(2^1))

Structural reading:

`16` is where the vertical idea becomes clearer.

The exponent `4` is not kept flat.

It is recursively expanded as:

    PET(4) = 2^PET(2)
           = 2^(2^1)

What PET makes visible:

- a power whose exponent is itself a power
- recursive height emerging from exponent structure
- a compact vertical description of repeated exponentiation structure

What PET does not make easier:

- evaluating the object still collapses to the ordinary value 16
- the representation is not evidence of faster arithmetic by itself

## Example 7: n = 64

Classical factorization:

    64 = 2^6

PET object:

    PET(64) = 2^PET(6)
            = 2^(2^1 * 3^1)

Structural reading:

The base has one root, but its exponent object has two roots:

    PET(6) = 2^1 * 3^1

What PET makes visible:

- a narrow top-level baseline
- a broader recursive exponent object
- breadth can move from value level into exponent level

What PET does not make easier:

- PET does not make the exponent 6 free to discover
- the recursive structure is only useful after the exponent structure is known

## Example 8: n = 72

Classical factorization:

    72 = 2^3 * 3^2

PET object:

    PET(72) = 2^PET(3) * 3^PET(2)
            = 2^(3^1) * 3^(2^1)

Structural reading:

Both top-level roots have non-leaf exponent objects.

The root `2` points to `PET(3)`.

The root `3` points to `PET(2)`.

What PET makes visible:

- two-root baseline
- non-leaf exponent objects on both roots
- cross-shaped exponent structure between 2 and 3

What PET does not make easier:

- this does not imply a shortcut for factoring 72
- it only shows how known factor structure becomes recursive object structure

## Example 9: n = 360

Classical factorization:

    360 = 2^3 * 3^2 * 5^1

PET object:

    PET(360) = 2^PET(3) * 3^PET(2) * 5^PET(1)
             = 2^(3^1) * 3^(2^1) * 5^1

Structural reading:

`360` has a three-root baseline:

    {2, 3, 5}

Two roots have non-leaf exponent objects.

One root has a leaf exponent object.

What PET makes visible:

- support topology: roots 2, 3, and 5
- exponent-object asymmetry across roots
- a structural distinction between breadth at the baseline and height inside
  exponent objects

What PET does not make easier:

- PET does not claim that 360 is easier to factor because of this notation
- PET only preserves recursive structure after the factorization is available

## Quick comparison

| n | Classical factorization | PET shape | Structural note |
|---|---|---|---|
| 1 | empty product | `1` | leaf object |
| 2 | `2^1` | `2^1` | one root with leaf exponent |
| 4 | `2^2` | `2^(2^1)` | exponent recursion begins |
| 8 | `2^3` | `2^(3^1)` | same root as 4, different exponent object |
| 16 | `2^4` | `2^(2^(2^1))` | exponent is itself vertically structured |
| 64 | `2^6` | `2^(2^1 * 3^1)` | narrow top level, broader exponent object |
| 72 | `2^3 * 3^2` | `2^(3^1) * 3^(2^1)` | two non-leaf exponent objects |
| 360 | `2^3 * 3^2 * 5^1` | `2^(3^1) * 3^(2^1) * 5^1` | baseline breadth plus exponent asymmetry |

This table is only a structural comparison.

It does not claim that PET discovers the factorization faster.

## Summary

The examples show the core PET distinction:

    numeric value != recursive structure

The classical factorization describes the final collapsed value.

The PET object keeps exponent structure recursively visible before collapse.

This may be useful for studying:

- height
- recursive shape
- structural identity
- baseline support
- exponent-object asymmetry
- addressable subobjects

But the construction boundary remains essential:

PET is not allowed to hide the cost of discovering prime-exponent structure.

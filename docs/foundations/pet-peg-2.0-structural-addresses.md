# PET/PEG 2.0 Structural Addresses and Identity

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


> **Superseded as the canonical address contract.** This note documents the
> current prime-label address implementation. Positional `@/…` paths and `^`
> slots are normatively defined in
> [`../reference/SPEC.md`](../reference/SPEC.md).
> Retain this document for legacy `PETObject` compatibility and research
> observations.

This note defines the PET/PEG 2.0 structural address and identity semantics.

A structural address identifies a location inside a recursive PET object.

The root object is addressed by:

    []

In code this is represented as:

    ()

Child objects are addressed by prime-label paths:

    [2]
    [2, 2]
    [3]
    [5]

In code these are represented as tuples:

    (2,)
    (2, 2)
    (3,)
    (5,)

This is PET/PEG 2.0 object semantics. It is not a routing policy, not a graph
traversal policy, and not a factorization-performance claim.

## Address syntax

A structural address is an ordered path of prime labels.

Examples for `60 = 2^2 * 3 * 5`:

| Address | Meaning |
| --- | --- |
| `[]` | root PET object for `60` |
| `[2]` | child object for `2^2` |
| `[2, 2]` | child object inside the exponent object `2` |
| `[3]` | child object for `3` |
| `[5]` | child object for `5` |

## Address validity

An address is valid when it resolves to an object inside the recursive PET
object.

Current implementation:

- `PETObject.at(address)`
- `PETObject.has_address(address)`
- `PETObject.addresses()`
- `PETObject.address_map()`
- `PETObject.address_resolution(address)`

Address resolution outcomes:

| Resolution | Meaning |
| --- | --- |
| `valid` | the address selects an object |
| `missing` | the address is absent |
| `blocked-at-leaf` | the address attempts to descend through an atomic leaf |

Example:

For `60 = 2^2 * 3 * 5`:

| Address | Resolution |
| --- | --- |
| `[]` | `valid` |
| `[2]` | `valid` |
| `[2, 2]` | `valid` |
| `[7]` | `missing` |
| `[3, 2]` | `blocked-at-leaf` |

## Selected object

The selected object is the PET object resolved by a valid address.

Example:

For `60 = 2^2 * 3 * 5`:

| Address | Selected object |
| --- | --- |
| `[]` | `PETObject(60)` |
| `[2]` | `PETObject(4)` |
| `[2, 2]` | `PETObject(2)` |
| `[3]` | `PETObject(3)` |
| `[5]` | `PETObject(5)` |

## Structural identity

PET/PEG 2.0 distinguishes shape equivalence from concrete structural identity.

Shape equivalence ignores values and prime labels.

Concrete structural identity preserves:

- role
- kind
- prime label
- address
- recursive child identity

Current implementation:

- `PETObject.structural_signature()`
- `PETObject.structural_identity_key()`
- `structurally_equivalent(left, right)`

Example:

`12 = 2^2 * 3` and `18 = 2 * 3^2` are structurally equivalent because both
have one recursive child and one atomic child.

But their concrete structural identity is different because the addressed prime
labels differ.

## Address outcomes across two objects

`compare_address(before, after, address)` classifies one address across two PET
objects.

Current outcomes:

| Outcome | Meaning |
| --- | --- |
| `stable` | valid before and after, same concrete structural identity |
| `created` | invalid before, valid after |
| `destroyed` | valid before, invalid after |
| `retargeted` | valid before and after, different concrete structural identity |
| `blocked-at-leaf` | address attempts to descend through an atomic leaf |
| `missing` | absent before and after without leaf blocking |

Important distinction:

`60 -> 12` at address `[2]` is stable.

Both objects select `2^2` at `[2]`.

`60 -> 24` at address `[2]` is retargeted.

The address is valid before and after, but the selected object changes:

    before: 2^2
    after:  2^3

So retargeted does not mean "the whole number changed." It means "the same
address now selects a different concrete object."

## Current implementation

Current implementation:

- `src/pet/object_model.py`
- `PETAddressError`
- `PETAddressComparison`
- `PETAddressResolution`
- `PETAddressOutcome`
- `PETObject.at(address)`
- `PETObject.walk()`
- `PETObject.addresses()`
- `PETObject.address_map()`
- `PETObject.has_address(address)`
- `PETObject.address_resolution(address)`
- `PETObject.structural_identity_key()`
- `compare_address(before, after, address)`

Current tests:

- `tests/test_object_model.py`

## Boundary

This semantics does not claim:

- routing policy
- graph traversal policy
- factorization performance
- stable CLI behavior changes

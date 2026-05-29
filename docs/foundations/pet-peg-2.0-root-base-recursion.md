# PET/PEG 2.0 Root-Base Recursion Semantics

This note defines the first PET/PEG 2.0 root-base recursion semantics.

Root-base recursion represents values as:

    N = R^K

where both `R` and `K` are PET/PEG 2.0 objects.

This is a PET/PEG 2.0 concept. It is not a routing policy, not an
anchor-selection policy, and not a factorization-performance claim.

## Exact root-base

A value has exact root-base form when the whole value is a perfect power.

For:

    N = p1^e1 * p2^e2 * ... * pn^en

the exact root-base exponent is:

    K = gcd(e1, e2, ..., en)

If `K > 1`, then:

    R = p1^(e1/K) * p2^(e2/K) * ... * pn^(en/K)

and:

    N = R^K

The exact form uses maximal exponent.

Examples:

| N | Exact root-base |
| ---: | --- |
| 16 | `2^4` |
| 64 | `2^6` |
| 81 | `3^4` |
| 216 | `6^3` |
| 65536 | `2^16` |
| 72 | none |

The maximal-exponent rule means:

    65536 = 2^16

not:

    256^2
    16^4
    4^8

## Base object and exponent object

In PET/PEG 2.0, the base and exponent are both recursive PET objects.

For:

    64 = 2^6 = 2^(2*3)

the root-base structure is:

    value = 64
    base_value = 2
    base_object = PETObject(2)
    exponent = 6
    exponent_object = PETObject(6)

The exponent is not treated as a dead integer. It participates in recursive PET
structure.

## Partial root-base components

A value may fail exact whole-object root-base form but still contain local exact
power components.

Example:

    72 = 2^3 * 3^2

The whole value is not exact root-base because:

    gcd(3, 2) = 1

But it contains partial root-base components:

| Address | Component |
| --- | --- |
| `(2,)` | `2^3` |
| `(3,)` | `3^2` |

Thus:

- exact root-base asks whether the whole object is `R^K`
- partial root-base reports local child components that are exact powers

More examples:

| N | Exact | Partial components |
| ---: | --- | --- |
| 30 | none | none |
| 64 | `2^6` | `(2,) -> 2^6` |
| 72 | none | `(2,) -> 2^3`, `(3,) -> 3^2` |
| 216 | `6^3` | `(2,) -> 2^3`, `(3,) -> 3^3` |

## Inferred root-base

`inferred` root-base is intentionally not implemented in this semantic layer.

Reason: inferred root-base requires a policy for guessing or preferring a
candidate structure when exact arithmetic evidence is incomplete or ambiguous.

That belongs to exploration policy, not to the core root-base object semantics.

For now:

- exact root-base is implemented
- partial root-base components are implemented
- inferred root-base is reserved
- inferred root-base must not be treated as a core fact until a separate policy
  defines how inference is made and verified

## Current implementation

Current implementation:

- `src/pet/root_base.py`
- `PETRootBase`
- `PETRootBaseComponent`
- `exact_root_base_from_int(n)`
- `partial_root_base_components_from_int(n)`

Current tests:

- `tests/test_root_base.py`

## Boundary

This semantics does not claim:

- improved factorization performance
- complete PEG algebra
- default routing changes
- anchor-selection changes
- stable CLI behavior changes
- inferred root-base support

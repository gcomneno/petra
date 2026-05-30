# PET/PEG 2.0 Operator Semantics

This note defines the first PET/PEG 2.0 operator semantics over recursive
`PETObject` values.

This layer defines target validity and value-level application for:

- `NEW`
- `DROP`
- `INC`
- `DEC`

It does not define routing policy, graph traversal policy, anchor selection, or
factorization-performance behavior.

## Operator axes

PET/PEG 2.0 currently defines two executable operator axes in the core object
model.

| Axis | Operators | Target kind |
| --- | --- | --- |
| X | `NEW`, `DROP` | parent-support |
| Y | `INC`, `DEC` | selected-root |

## X-axis operators

X-axis operators mutate support at an addressed parent PET object.

### NEW(parent_address, q)

`NEW` adds a fresh prime label `q` to the support of the parent object selected
by `parent_address`.

Target validity:

- `parent_address` must resolve to a valid PET object
- selected parent must be composite
- `q` must be prime
- `q` must not already exist in the selected parent support

Example on `60 = 2^2 * 3 * 5`:

    NEW((), 7)

is valid and produces:

    60 -> 420

Nested example:

    NEW((2,), 3)

enters the exponent-object of the selected root `2`.

For:

    60 = 2^2 * 3 * 5

the selected child at `(2,)` has exponent object `2`.

Adding `3` inside that exponent object changes:

    2 -> 2 * 3 = 6

so:

    2^2 * 3 * 5 -> 2^6 * 3 * 5 = 960

### DROP(parent_address, p)

`DROP` removes an existing prime label `p` from the support of the parent object
selected by `parent_address`.

Target validity:

- `parent_address` must resolve to a valid PET object
- selected parent must be composite
- `p` must be prime
- `p` must exist in the selected parent support

Example on `60 = 2^2 * 3 * 5`:

    DROP((), 5)

is valid and produces:

    60 -> 12

## Y-axis operators

Y-axis operators mutate the exponent of a selected root.

### INC(address)

`INC` increments the exponent of the root selected by `address`.

Target validity:

- `address` must be non-empty
- `address` must resolve to a valid selected root
- atomic and composite selected roots are both valid targets

Example on `60 = 2^2 * 3 * 5`:

    INC((2,))

increments the exponent of `2`:

    2^2 -> 2^3

so:

    60 -> 120

Nested example:

    INC((2, 2))

increments inside the exponent-object of root `2`.

For:

    60 = 2^2 * 3 * 5

the exponent object of `2` is itself the PET object for `2`. Incrementing that
inner root changes the exponent object:

    2 -> 2^2 = 4

so the outer exponent changes from `2` to `4`:

    2^2 * 3 * 5 -> 2^4 * 3 * 5 = 240

When applied through the current value-level implementation, recursive exponent
rewriting is rebuilt through represented integer value.

### DEC(address)

`DEC` decrements the exponent of the root selected by `address`.

Target validity:

- `address` must be non-empty
- `address` must resolve to a valid selected root
- selected root must be composite
- selected atomic leaf is invalid because exponent `1` has no predecessor in
  this semantics

Example on `60 = 2^2 * 3 * 5`:

    DEC((2,))

decrements the exponent of `2`:

    2^2 -> 2^1

so:

    60 -> 30

`DEC((3,))` is invalid because `(3,)` selects an atomic leaf.

## Target semantics

Current implementation resolves operator targets without mutation.

Implementation:

- `PETOperatorTarget`
- `new_target(obj, parent_address, q)`
- `drop_target(obj, parent_address, p)`
- `inc_target(obj, address)`
- `dec_target(obj, address)`
- `resolve_operator_target(obj, op, address, argument=None)`

Target examples on `PETObject(60)`:

| Invocation | Valid | Reason |
| --- | --- | --- |
| `NEW((), 7)` | yes | `new-target-valid` |
| `NEW((), 3)` | no | `q-already-in-target-baseline` |
| `DROP((), 5)` | yes | `drop-target-valid` |
| `DROP((), 7)` | no | `p-not-in-target-baseline` |
| `INC((2,))` | yes | `inc-target-valid` |
| `INC((3, 2))` | no | `address-blocked-at-leaf` |
| `DEC((2,))` | yes | `dec-target-valid` |
| `DEC((3,))` | no | `selected-object-is-atomic-leaf` |

## Value-level application

Current implementation applies valid operators by represented integer value and
then rebuilds a new `PETObject`.

Implementation:

- `PETOperatorApplication`
- `apply_operator_by_value(obj, op, address, argument=None)`

This is intentionally value-level application.

It is not yet manual structural rewriting of existing object internals.

Application examples on `PETObject(60)`:

| Invocation | Result |
| --- | --- |
| `NEW((), 7)` | `60 -> 420` |
| `DROP((), 5)` | `60 -> 12` |
| `INC((2,))` | `60 -> 120` |
| `DEC((2,))` | `60 -> 30` |
| `INC((2, 2))` | `60 -> 240` |
| `NEW((2,), 3)` | `60 -> 960` |

Invalid operators return an invalid `PETOperatorApplication` without producing
an `after_object`.

## Current implementation

Current implementation:

- `src/pet/operators.py`
- `PETOperatorTarget`
- `PETOperatorApplication`
- `new_target`
- `drop_target`
- `inc_target`
- `dec_target`
- `resolve_operator_target`
- `apply_operator_by_value`

Current tests:

- `tests/test_operators.py`

## Boundary

This semantics does not claim:

- routing policy
- graph traversal policy
- anchor selection
- factorization performance
- stable CLI behavior changes
- manual structural rewrite semantics

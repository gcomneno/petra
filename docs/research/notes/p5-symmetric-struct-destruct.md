# Symmetric struct/destruct (P5)

Status: research note (bounded empirical)
Scope: extend struct with inner-container hook and verify
       invertibility of struct/destruct
Stability: positive result on the tested cases; no proof for all shapes
Thread: P5

## Context

`t01-struct-destruct-exponential.md` records a limit of `struct`: it
adds fathers only at the root, or replaces a leaf with a container.
When `destruct` detaches a father of an inner container, `struct(rest,
piece)` does not recompose the original shape. This was seen for
`12^3 = 1728`.

P5 asks whether adding a fourth hook (inner-container append/prepend)
restores invertibility.

## Phase A — extend struct

A new keyword `inner: bool = False` is added to `struct`. When `True`,
`struct` also tries append and prepend on every container reachable as
an exponent, at any depth. When `False`, behaviour is unchanged.

New helpers:

- `_inner_container_addresses(shape)`: addresses of inner containers;
- `_append_father_at(shape, address, b, at_end)`: append or prepend a
  father to the container at `address`.

The special case `b = Leaf` also gains inner support.

## Phase B — invertibility

For each `(piece, rest, kind)` in `destruct(s)`, check whether
`s in struct(rest, piece, inner=True)`.

Tested on four pairs:

| pair | shape | cases | failures |
| --- | --- | ---: | ---: |
| 12^3 | `○^(A^(A × B) × B^(A))` | 5 | 0 |
| 30^2 | `○^(A^(A) × B^(A) × C^(A))` | 4 | 0 |
| 30^3 | `○^(A^(A) × B^(A) × C^(A))` | 4 | 0 |
| 6^4 | `○^(A^(A^(A)) × B^(A^(A)))` | 3 | 0 |

Zero failures. The fourth hook resolves the case found in T01.

## Tests

`resolver/tests/test_struct_destruct_inner.py` adds four tests:

- default `inner=False` preserves old behaviour;
- `inner=True` adds cases;
- `destruct` is invertible with `inner=True` on six shapes;
- inner append on a nested container is reached.

All pass together with the existing tests: 14/14.

## Boundary

This note does not claim:

- that `struct` is now exactly inverse to `destruct` for all shapes
  (tested on four pairs plus six shapes);
- that the new hook is minimal or optimal;
- that other limits of `struct` (beyond inner containers) do not
  exist.

## Reproducibility

`python tools/research/t01_exponential_struct_destruct.py` with the
new `inner=True` parameter, or the inner test file directly.

## Status

P5 closed. Phase A implemented, phase B verified on the tested cases.

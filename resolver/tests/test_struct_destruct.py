"""Tests for struct and destruct."""

from __future__ import annotations

from petra import parse_shape
from resolver.struct_destruct import destruct, struct


# ---------------------------------------------------------------------------
# destruct
# ---------------------------------------------------------------------------


def test_destruct_leaf_is_empty() -> None:
    assert destruct(parse_shape("1")) == frozenset()


def test_destruct_flat_container_is_empty() -> None:
    # all exponents are implicit leaves
    assert destruct(parse_shape("C(r0^1)")) == frozenset()
    assert destruct(parse_shape("C(r0^1,r1^1)")) == frozenset()
    assert destruct(parse_shape("C(r0^1,r1^1,r2^1)")) == frozenset()


def test_destruct_one_level_nesting() -> None:
    # C(r0^C(r0^1)) -> one pair: (C(r0^1), C(r0^1))
    a = parse_shape("C(r0^C(r0^1))")
    pairs = destruct(a)
    assert pairs == frozenset(
        {
            (parse_shape("C(r0^1)"), parse_shape("C(r0^1)")),
        }
    )


def test_destruct_two_terms_one_nested() -> None:
    # C(r0^C(r0^1),r1^1) -> one pair
    a = parse_shape("C(r0^C(r0^1),r1^1)")
    pairs = destruct(a)
    assert pairs == frozenset(
        {
            (
                parse_shape("C(r0^1,r1^1)"),
                parse_shape("C(r0^1)"),
            ),
        }
    )


def test_destruct_two_nested_terms() -> None:
    # C(r0^C(r0^1),r1^C(r0^1)) -> two pairs
    a = parse_shape("C(r0^C(r0^1),r1^C(r0^1))")
    pairs = destruct(a)
    assert pairs == frozenset(
        {
            (
                parse_shape("C(r0^1,r1^C(r0^1))"),
                parse_shape("C(r0^1)"),
            ),
            (
                parse_shape("C(r0^C(r0^1),r1^1)"),
                parse_shape("C(r0^1)"),
            ),
        }
    )


def test_destruct_does_not_recurse_into_detached() -> None:
    # C(r0^C(r0^C(r0^1))) -> one pair, one level
    a = parse_shape("C(r0^C(r0^C(r0^1)))")
    pairs = destruct(a)
    assert pairs == frozenset(
        {
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^C(r0^1))"),
            ),
        }
    )


# ---------------------------------------------------------------------------
# struct
# ---------------------------------------------------------------------------


def test_struct_leaf_a_replaces_mother() -> None:
    # struct(○, B) = {B}: the mother hook replaces itself with B
    b = parse_shape("C(r0^1)")
    assert struct(parse_shape("1"), b) == frozenset({b})


def test_struct_leaf_b_adds_leaf_father() -> None:
    # struct(A, ○) returns:
    # - {A}: identity (replace with a leaf is a no-op)
    # - append: a new leaf father at the tail
    # - prepend: a new leaf father at the head
    # If A has only leaf fathers, append and prepend collapse, so the
    # result may have fewer than three elements.
    a = parse_shape("C(r0^C(r0^1))")   # ○^(A^(A))
    result = struct(a, parse_shape("1"))
    # identity + append + prepend
    assert parse_shape("C(r0^C(r0^1))") in result          # identity
    assert parse_shape("C(r0^C(r0^1),r1^1)") in result     # append
    assert parse_shape("C(r0^1,r1^C(r0^1))") in result     # prepend
    assert len(result) == 3


def test_struct_leaf_b_on_all_leaf_fathers_collapses() -> None:
    # A = ○^(A × B): append and prepend produce the same shape
    # because leaf fathers are indistinguishable.
    a = parse_shape("C(r0^1,r1^1)")
    result = struct(a, parse_shape("1"))
    assert len(result) == 2
    assert parse_shape("C(r0^1,r1^1)") in result          # identity
    assert parse_shape("C(r0^1,r1^1,r2^1)") in result     # append == prepend


def test_struct_leaf_leaf_is_leaf() -> None:
    assert struct(parse_shape("1"), parse_shape("1")) == frozenset({parse_shape("1")})


def test_struct_single_father_has_three_attachment_points() -> None:
    # A = C(r0^1) has: one leaf (r0) + tail hook + head hook = 3 points
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^C(r0^1))")
    result = struct(a, b)
    assert result == frozenset(
        {
            # replacement of the leaf of r0 by b
            parse_shape("C(r0^C(r0^C(r0^1)))"),
            # append b as a new father at the end
            parse_shape("C(r0^1,r1^C(r0^C(r0^1)))"),
            # prepend b as a new father at the beginning
            parse_shape("C(r0^C(r0^C(r0^1)),r1^1)"),
        }
    )


def test_struct_two_fathers_have_four_attachment_points() -> None:
    # A = C(r0^1,r1^1): two leaves + tail + head = 4 points
    a = parse_shape("C(r0^1,r1^1)")
    b = parse_shape("C(r0^C(r0^1))")
    assert len(struct(a, b)) == 4


def test_struct_only_considers_first_level_attachments() -> None:
    # A = C(r0^1, r1^C(r0^1), r2^1):
    # implicit-leaf terms of the root container are r0 and r2 only.
    # The leaf inside r1's explicit exponent is NOT an attachment point.
    # Plus tail and head: 4 points total.
    a = parse_shape("C(r0^1,r1^C(r0^1),r2^1)")
    b = parse_shape("C(r0^C(r0^1))")
    assert len(struct(a, b)) == 4


# ---------------------------------------------------------------------------
# inverse law
# ---------------------------------------------------------------------------


def test_destruct_then_struct_recovers_a() -> None:
    for text in [
        "C(r0^C(r0^1))",
        "C(r0^C(r0^1),r1^1)",
        "C(r0^1,r1^C(r0^1))",
        "C(r0^C(r0^C(r0^1)))",
        "C(r0^C(r0^1),r1^C(r0^1))",
    ]:
        a = parse_shape(text)
        for b, c in destruct(a):
            assert a in struct(b, c), f"failed for {text}"

"""Tests for compose and decompose."""

from __future__ import annotations

from petra import parse_shape
from resolver.struct_destruct import compose, decompose


# ---------------------------------------------------------------------------
# decompose
# ---------------------------------------------------------------------------


def test_decompose_leaf_is_empty() -> None:
    assert decompose(parse_shape("1")) == frozenset()


def test_decompose_flat_container_is_empty() -> None:
    # all exponents are implicit leaves
    assert decompose(parse_shape("C(r0^1)")) == frozenset()
    assert decompose(parse_shape("C(r0^1,r1^1)")) == frozenset()
    assert decompose(parse_shape("C(r0^1,r1^1,r2^1)")) == frozenset()


def test_decompose_one_level_nesting() -> None:
    # C(r0^C(r0^1)) -> one pair: (C(r0^1), C(r0^1))
    a = parse_shape("C(r0^C(r0^1))")
    pairs = decompose(a)
    assert pairs == frozenset(
        {
            (parse_shape("C(r0^1)"), parse_shape("C(r0^1)")),
        }
    )


def test_decompose_two_terms_one_nested() -> None:
    # C(r0^C(r0^1),r1^1) -> one pair
    a = parse_shape("C(r0^C(r0^1),r1^1)")
    pairs = decompose(a)
    assert pairs == frozenset(
        {
            (
                parse_shape("C(r0^1,r1^1)"),
                parse_shape("C(r0^1)"),
            ),
        }
    )


def test_decompose_two_nested_terms() -> None:
    # C(r0^C(r0^1),r1^C(r0^1)) -> two pairs
    a = parse_shape("C(r0^C(r0^1),r1^C(r0^1))")
    pairs = decompose(a)
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


def test_decompose_does_not_recurse_into_detached() -> None:
    # C(r0^C(r0^C(r0^1))) -> one pair, one level
    a = parse_shape("C(r0^C(r0^C(r0^1)))")
    pairs = decompose(a)
    assert pairs == frozenset(
        {
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^C(r0^1))"),
            ),
        }
    )


# ---------------------------------------------------------------------------
# compose
# ---------------------------------------------------------------------------


def test_compose_leaf_a_gives_empty() -> None:
    # A = Leaf has no attachment points
    assert compose(parse_shape("1"), parse_shape("C(r0^1)")) == frozenset()


def test_compose_single_attachment() -> None:
    # A = C(r0^1) has one attachment point (r0)
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^C(r0^1))")
    assert compose(a, b) == frozenset({parse_shape("C(r0^C(r0^C(r0^1)))")})


def test_compose_two_attachments() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    b = parse_shape("C(r0^C(r0^1))")
    assert compose(a, b) == frozenset(
        {
            parse_shape("C(r0^C(r0^C(r0^1)),r1^1)"),
            parse_shape("C(r0^1,r1^C(r0^C(r0^1)))"),
        }
    )


def test_compose_only_considers_first_level_attachments() -> None:
    # A = C(r0^1, r1^C(r0^1), r2^1):
    # implicit-leaf terms of the root container are r0 and r2 only.
    # The leaf inside r1's explicit exponent is NOT an attachment point.
    a = parse_shape("C(r0^1,r1^C(r0^1),r2^1)")
    b = parse_shape("C(r0^C(r0^1))")
    assert len(compose(a, b)) == 2


# ---------------------------------------------------------------------------
# inverse law
# ---------------------------------------------------------------------------


def test_decompose_then_compose_recovers_a() -> None:
    for text in [
        "C(r0^C(r0^1))",
        "C(r0^C(r0^1),r1^1)",
        "C(r0^1,r1^C(r0^1))",
        "C(r0^C(r0^C(r0^1)))",
        "C(r0^C(r0^1),r1^C(r0^1))",
    ]:
        a = parse_shape(text)
        for b, c in decompose(a):
            assert a in compose(b, c), f"failed for {text}"

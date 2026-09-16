"""Tests for struct and destruct."""

from __future__ import annotations

from petra import parse_shape

from resolver.struct_destruct import destruct, struct

# ---------------------------------------------------------------------------
# destruct
# ---------------------------------------------------------------------------


def test_destruct_leaf_is_empty() -> None:
    assert destruct(parse_shape("1")) == frozenset()


def test_destruct_single_father_is_empty() -> None:
    assert destruct(parse_shape("C(r0^1)")) == frozenset()


def test_destruct_flat_two_fathers_has_one_father_case() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    result = destruct(a)
    assert result == frozenset(
        {
            (parse_shape("1"), parse_shape("C(r0^1)"), "father"),
        }
    )


def test_destruct_flat_three_fathers_has_one_father_case() -> None:
    a = parse_shape("C(r0^1,r1^1,r2^1)")
    result = destruct(a)
    assert result == frozenset(
        {
            (parse_shape("1"), parse_shape("C(r0^1,r1^1)"), "father"),
        }
    )


def test_destruct_one_level_nesting() -> None:
    a = parse_shape("C(r0^C(r0^1))")
    result = destruct(a)
    assert result == frozenset(
        {
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^1)"),
                "exponent",
            ),
        }
    )


def test_destruct_two_terms_one_nested() -> None:
    a = parse_shape("C(r0^C(r0^1),r1^1)")
    result = destruct(a)
    assert result == frozenset(
        {
            # exponent on the first father
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^1,r1^1)"),
                "exponent",
            ),
            # father 0: exponent is C(r0^1)
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^1)"),
                "father",
            ),
            # father 1: exponent is Leaf
            (
                parse_shape("1"),
                parse_shape("C(r0^C(r0^1))"),
                "father",
            ),
        }
    )


def test_destruct_two_nested_terms() -> None:
    a = parse_shape("C(r0^C(r0^1),r1^C(r0^1))")
    result = destruct(a)
    assert result == frozenset(
        {
            # exponent on the first father
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^1,r1^C(r0^1))"),
                "exponent",
            ),
            # exponent on the second father
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^C(r0^1),r1^1)"),
                "exponent",
            ),
            # father 0: exponent is C(r0^1)
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^C(r0^1))"),
                "father",
            ),
            # father 1: exponent is C(r0^1)
            (
                parse_shape("C(r0^1)"),
                parse_shape("C(r0^C(r0^1))"),
                "father",
            ),
        }
    )


def test_destruct_does_not_recurse_into_detached() -> None:
    a = parse_shape("C(r0^C(r0^C(r0^1)))")
    result = destruct(a)
    assert result == frozenset(
        {
            (
                parse_shape("C(r0^C(r0^1))"),
                parse_shape("C(r0^1)"),
                "exponent",
            ),
        }
    )


# ---------------------------------------------------------------------------
# struct
# ---------------------------------------------------------------------------


def test_struct_leaf_a_replaces_mother() -> None:
    b = parse_shape("C(r0^1)")
    assert struct(parse_shape("1"), b) == frozenset({b})


def test_destruct_then_struct_recovers_a() -> None:
    for text in [
        "C(r0^C(r0^1))",
        "C(r0^C(r0^1),r1^1)",
        "C(r0^1,r1^C(r0^1))",
        "C(r0^C(r0^C(r0^1)))",
        "C(r0^C(r0^1),r1^C(r0^1))",
        "C(r0^1,r1^1)",
        "C(r0^1,r1^1,r2^1)",
    ]:
        a = parse_shape(text)
        for piece, rest, kind in destruct(a):
            assert a in struct(rest, piece), (
                f"failed for {text} (kind={kind})"
            )

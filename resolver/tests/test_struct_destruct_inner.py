"""Tests for the inner-container hook of struct."""

from __future__ import annotations

from petra import parse_shape
from resolver.struct_destruct import destruct, struct


def test_struct_inner_default_is_old_behaviour() -> None:
    # default inner=False: same result as before
    a = parse_shape("C(r0^C(r0^1))")
    b = parse_shape("C(r0^1)")
    senza = struct(a, b)
    senza_esplicito = struct(a, b, inner=False)
    assert senza == senza_esplicito


def test_struct_inner_adds_new_cases() -> None:
    a = parse_shape("C(r0^C(r0^1))")
    b = parse_shape("C(r0^1)")
    senza = struct(a, b)
    con = struct(a, b, inner=True)
    assert senza <= con
    assert len(con) >= len(senza)


def test_destruct_invertible_with_inner() -> None:
    for text in [
        "C(r0^C(r0^1))",
        "C(r0^C(r0^1),r1^1)",
        "C(r0^C(r0^1),r1^C(r0^1))",
        "C(r0^C(r0^C(r0^1)))",
        "C(r0^C(r0^1),r1^C(r0^1))",
        "C(r0^1,r1^1)",
    ]:
        a = parse_shape(text)
        for piece, rest, kind in destruct(a):
            recovered = struct(rest, piece, inner=True)
            assert a in recovered, f"failed for {text} (kind={kind})"


def test_inner_prepend_and_append_on_nested() -> None:
    a = parse_shape("C(r0^C(r0^1))")
    b = parse_shape("C(r0^1)")
    results = struct(a, b, inner=True)
    # expected: at least one result with b grafted on the inner container
    # inner container is C(r0^1). Appending gives C(r0^1, r1^C(r0^1)).
    expected = parse_shape("C(r0^C(r0^1,r1^C(r0^1)))")
    assert expected in results

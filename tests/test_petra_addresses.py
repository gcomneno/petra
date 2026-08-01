"""Contract tests for PETRA positional structural addresses."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from itertools import product

import pytest

from petra import (
    Address,
    AddressError,
    Container,
    Leaf,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    Root,
    Term,
    parse_address,
    render_address,
    resolve_address,
    to_canonical_data,
)


def term(rank: int, exponent: Leaf | Container) -> Term:
    return Term(root=Root(rank), exponent=exponent)


def container(*exponents: Leaf | Container) -> Container:
    return Container(
        terms=tuple(
            term(rank, exponent)
            for rank, exponent in enumerate(exponents)
        )
    )


def sample_shape() -> Container:
    return container(
        container(
            Leaf(),
            container(Leaf()),
        ),
        Leaf(),
        Leaf(),
    )


def malformed_reason(value: object) -> str:
    with pytest.raises(AddressError) as error:
        parse_address(value)

    return error.value.reason


def resolution_reason(
    shape: object,
    address: object,
) -> str:
    with pytest.raises(AddressError) as error:
        resolve_address(shape, address)

    return error.value.reason


def test_address_model_is_minimal_and_immutable() -> None:
    assert [field.name for field in fields(Address)] == [
        "indices",
        "is_slot",
    ]

    anchor = Address()
    term_address = Address(indices=(0, 2))
    slot_address = Address(indices=(0, 2), is_slot=True)

    assert anchor.kind == "anchor"
    assert term_address.kind == "term"
    assert slot_address.kind == "slot"

    with pytest.raises(FrozenInstanceError):
        term_address.indices = (1,)

    with pytest.raises(FrozenInstanceError):
        slot_address.is_slot = False


@pytest.mark.parametrize(
    ("indices", "is_slot", "exception"),
    [
        ([0], False, TypeError),
        ((True,), False, TypeError),
        ((1.0,), False, TypeError),
        (("1",), False, TypeError),
        ((-1,), False, ValueError),
        ((), True, ValueError),
        ((0,), 1, TypeError),
        ((0,), "yes", TypeError),
    ],
)
def test_address_constructor_rejects_noncanonical_state(
    indices: object,
    is_slot: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        Address(indices=indices, is_slot=is_slot)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("@/", Address()),
        ("@/0", Address(indices=(0,))),
        ("@/10", Address(indices=(10,))),
        ("@/0/1", Address(indices=(0, 1))),
        (
            "@/12/0/345",
            Address(indices=(12, 0, 345)),
        ),
        (
            "@/0/^",
            Address(indices=(0,), is_slot=True),
        ),
        (
            "@/0/1/^",
            Address(indices=(0, 1), is_slot=True),
        ),
    ],
)
def test_valid_addresses_parse_and_render_canonically(
    text: str,
    expected: Address,
) -> None:
    parsed = parse_address(text)

    assert parsed == expected
    assert render_address(parsed) == text
    assert str(parsed) == text


@pytest.mark.parametrize(
    "text",
    [
        "",
        "@",
        "/",
        "@//",
        "@///",
        "@//0",
        "@/0/",
        "@/0//1",
        "@/00",
        "@/01",
        "@/000",
        "@/-1",
        "@/+1",
        "@/ 1",
        "@/1 ",
        "@/1.0",
        "@/a",
        "@/١",
        "@/１",
        "@/^",
        "@/0^",
        "@/0/^^",
        "@/0/^/",
        "@/0/^/1",
        "@/0/1/^/2",
        "@/0//^",
        " @/0",
        "@/0 ",
        "@/0\n",
    ],
)
def test_malformed_text_uses_stable_reason(text: str) -> None:
    assert malformed_reason(text) == "address-malformed"


@pytest.mark.parametrize(
    "value",
    [
        None,
        0,
        1.5,
        b"@/0",
        ["@/0"],
    ],
)
def test_non_text_input_is_malformed(value: object) -> None:
    assert malformed_reason(value) == "address-malformed"


def test_address_error_exposes_the_stable_reason() -> None:
    with pytest.raises(AddressError) as error:
        parse_address("@/00")

    assert error.value.reason == "address-malformed"
    assert str(error.value) == "address-malformed"
    assert error.value.args == ("address-malformed",)


def test_render_requires_an_address_value() -> None:
    with pytest.raises(TypeError, match="Address"):
        render_address("@/0")


def test_generated_addresses_round_trip_deterministically() -> None:
    addresses = [Address()]

    for depth in range(1, 5):
        for indices in product(range(3), repeat=depth):
            addresses.append(Address(indices=indices))
            addresses.append(
                Address(indices=indices, is_slot=True)
            )

    for address in addresses:
        rendered = render_address(address)

        assert parse_address(rendered) == address
        assert render_address(parse_address(rendered)) == rendered


@pytest.mark.parametrize(
    "shape",
    [
        Leaf(),
        sample_shape(),
    ],
)
def test_anchor_resolves_for_every_root_shape(
    shape: Leaf | Container,
) -> None:
    resolved = resolve_address(shape, "@/")

    assert isinstance(resolved, ResolvedAnchor)
    assert resolved.kind == "anchor"
    assert resolved.address == Address()
    assert resolved.shape is shape


def test_term_addresses_resolve_selected_terms() -> None:
    shape = sample_shape()

    root_term = resolve_address(shape, "@/0")
    nested_term = resolve_address(shape, "@/0/1")
    deep_term = resolve_address(shape, "@/0/1/0")

    assert isinstance(root_term, ResolvedTerm)
    assert root_term.address == Address(indices=(0,))
    assert root_term.term is shape.terms[0]

    assert isinstance(nested_term, ResolvedTerm)
    assert nested_term.address == Address(indices=(0, 1))
    assert nested_term.term is shape.terms[0].exponent.terms[1]

    assert isinstance(deep_term, ResolvedTerm)
    assert deep_term.address == Address(indices=(0, 1, 0))
    assert (
        deep_term.term
        is shape.terms[0].exponent.terms[1].exponent.terms[0]
    )


def test_term_resolution_does_not_project_the_final_exponent() -> None:
    shape = sample_shape()

    resolved = resolve_address(shape, "@/0/1")

    assert isinstance(resolved, ResolvedTerm)
    assert isinstance(resolved.term.exponent, Container)


def test_slot_resolution_supports_latent_and_materialized_relations() -> None:
    shape = sample_shape()

    latent = resolve_address(shape, "@/0/0/^")
    materialized = resolve_address(shape, "@/0/1/^")

    latent_owner = shape.terms[0].exponent.terms[0]
    materialized_owner = shape.terms[0].exponent.terms[1]

    assert isinstance(latent, ResolvedSlot)
    assert latent.owner is latent_owner
    assert latent.target is latent_owner.exponent
    assert isinstance(latent.target, Leaf)

    assert isinstance(materialized, ResolvedSlot)
    assert materialized.owner is materialized_owner
    assert materialized.target is materialized_owner.exponent
    assert isinstance(materialized.target, Container)


def test_resolution_records_are_minimal_and_immutable() -> None:
    shape = sample_shape()

    anchor = resolve_address(shape, "@/")
    selected_term = resolve_address(shape, "@/1")
    slot = resolve_address(shape, "@/0/0/^")

    assert [field.name for field in fields(ResolvedAnchor)] == [
        "address",
        "shape",
    ]
    assert [field.name for field in fields(ResolvedTerm)] == [
        "address",
        "term",
    ]
    assert [field.name for field in fields(ResolvedSlot)] == [
        "address",
        "owner",
        "target",
    ]

    with pytest.raises(FrozenInstanceError):
        anchor.shape = Leaf()

    with pytest.raises(FrozenInstanceError):
        selected_term.term = shape.terms[0]

    with pytest.raises(FrozenInstanceError):
        slot.target = Leaf()


def test_repeated_leaf_terms_are_selected_only_by_position() -> None:
    shape = container(Leaf(), Leaf(), Leaf())

    first = resolve_address(shape, "@/0")
    second = resolve_address(shape, "@/1")
    third = resolve_address(shape, "@/2")

    assert isinstance(first, ResolvedTerm)
    assert isinstance(second, ResolvedTerm)
    assert isinstance(third, ResolvedTerm)

    assert first.term is shape.terms[0]
    assert second.term is shape.terms[1]
    assert third.term is shape.terms[2]


@pytest.mark.parametrize(
    "address",
    [
        "@/0",
        "@/1",
        "@/2",
        "@/0/0",
        "@/0/1",
        "@/0/1/0",
        "@/0/0/^",
        "@/0/1/^",
        "@/0/1/0/^",
    ],
)
def test_equivalent_shapes_resolve_equivalent_targets(
    address: str,
) -> None:
    left = sample_shape()
    right = sample_shape()

    assert left == right
    assert left is not right
    assert resolve_address(left, address) == resolve_address(
        right,
        address,
    )


@pytest.mark.parametrize(
    "address",
    [
        "@/0",
        "@/1",
        "@/999",
        "@/0/^",
    ],
)
def test_root_leaf_has_no_selectable_terms(address: str) -> None:
    assert (
        resolution_reason(Leaf(), address)
        == "address-out-of-range"
    )


@pytest.mark.parametrize(
    "address",
    [
        "@/3",
        "@/999",
        "@/0/2",
        "@/0/1/1",
        "@/0/1/999",
    ],
)
def test_missing_terms_are_out_of_range(address: str) -> None:
    assert (
        resolution_reason(sample_shape(), address)
        == "address-out-of-range"
    )


@pytest.mark.parametrize(
    "address",
    [
        "@/1/0",
        "@/2/0",
        "@/0/0/0",
        "@/0/0/999",
        "@/0/0/0/^",
    ],
)
def test_continuing_through_leaf_uses_crosses_leaf(
    address: str,
) -> None:
    assert (
        resolution_reason(sample_shape(), address)
        == "address-crosses-leaf"
    )


def test_resolution_failure_precedence_is_deterministic() -> None:
    assert (
        resolution_reason(
            container(Leaf()),
            "@/0/999999",
        )
        == "address-crosses-leaf"
    )

    assert (
        resolution_reason(
            container(container(Leaf())),
            "@/1/0/0",
        )
        == "address-out-of-range"
    )


@pytest.mark.parametrize(
    "address",
    [
        "not-an-address",
        "@/999",
    ],
)
def test_shape_validation_precedes_parsing_and_traversal(
    address: str,
) -> None:
    malformed_shape = Container(
        terms=(
            Term(root=Root(1), exponent=Leaf()),
        )
    )

    with pytest.raises(
        ValueError,
        match="non-canonical root rank",
    ) as error:
        resolve_address(malformed_shape, address)

    assert not isinstance(error.value, AddressError)


def test_resolution_never_normalizes_or_mutates_shape() -> None:
    shape = sample_shape()
    before_data = to_canonical_data(shape)
    before_terms = shape.terms

    resolve_address(shape, "@/0/1/0/^")

    assert to_canonical_data(shape) == before_data
    assert shape.terms is before_terms
    assert shape.terms[0].root == Root(0)
    assert shape.terms[1].root == Root(1)
    assert shape.terms[2].root == Root(2)


def test_failed_resolution_preserves_exact_shape() -> None:
    shape = sample_shape()
    before_data = to_canonical_data(shape)
    before_terms = shape.terms

    assert (
        resolution_reason(shape, "@/1/0")
        == "address-crosses-leaf"
    )

    assert to_canonical_data(shape) == before_data
    assert shape.terms is before_terms


def test_resolution_rejects_non_petra_shape_before_parsing() -> None:
    with pytest.raises(
        TypeError,
        match="expected a PETRA Leaf or Container",
    ) as error:
        resolve_address(object(), "not-an-address")

    assert not isinstance(error.value, AddressError)



def test_address_error_accepts_only_normative_reasons() -> None:
    for reason in (
        "address-malformed",
        "address-out-of-range",
        "address-crosses-leaf",
    ):
        error = AddressError(reason)

        assert error.reason == reason
        assert error.args == (reason,)

    with pytest.raises(
        ValueError,
        match="unknown address reason",
    ):
        AddressError("address-kind-mismatch")

    with pytest.raises(
        TypeError,
        match="address reason must be a str",
    ):
        AddressError(None)


def test_resolved_anchor_rejects_inconsistent_state() -> None:
    with pytest.raises(
        ValueError,
        match="anchor address",
    ):
        ResolvedAnchor(
            address=Address(indices=(0,)),
            shape=Leaf(),
        )

    with pytest.raises(
        TypeError,
        match="expected a PETRA Leaf or Container",
    ):
        ResolvedAnchor(
            address=Address(),
            shape=object(),
        )


def test_resolved_term_rejects_inconsistent_state() -> None:
    selected = term(0, Leaf())

    with pytest.raises(
        ValueError,
        match="term address",
    ):
        ResolvedTerm(
            address=Address(),
            term=selected,
        )

    with pytest.raises(
        TypeError,
        match="resolved term value must be a Term",
    ):
        ResolvedTerm(
            address=Address(indices=(0,)),
            term=object(),
        )

    with pytest.raises(
        ValueError,
        match="rank does not match",
    ):
        ResolvedTerm(
            address=Address(indices=(1,)),
            term=selected,
        )


def test_resolved_slot_rejects_inconsistent_state() -> None:
    owner = term(0, container(Leaf()))

    with pytest.raises(
        ValueError,
        match="slot address",
    ):
        ResolvedSlot(
            address=Address(indices=(0,)),
            owner=owner,
            target=owner.exponent,
        )

    with pytest.raises(
        TypeError,
        match="resolved slot owner must be a Term",
    ):
        ResolvedSlot(
            address=Address(
                indices=(0,),
                is_slot=True,
            ),
            owner=object(),
            target=Leaf(),
        )

    with pytest.raises(
        ValueError,
        match="rank does not match",
    ):
        ResolvedSlot(
            address=Address(
                indices=(1,),
                is_slot=True,
            ),
            owner=owner,
            target=owner.exponent,
        )

    with pytest.raises(
        ValueError,
        match="owner exponent",
    ):
        ResolvedSlot(
            address=Address(
                indices=(0,),
                is_slot=True,
            ),
            owner=owner,
            target=container(Leaf()),
        )

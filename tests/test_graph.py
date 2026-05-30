from pet import (
    PETGraphEdge,
    PETGraphNode,
    operator_applications_by_value,
    operator_label,
    operator_neighbors_by_value,
    pet_object_from_int,
)


def test_operator_label_formats_addressed_operator_invocations() -> None:
    assert operator_label("NEW", (), 7) == "NEW(parent_address=[],q=7)"
    assert operator_label("DROP", (2,), 3) == "DROP(parent_address=[2],p=3)"
    assert operator_label("INC", (2, 2)) == "INC(address=[2, 2])"
    assert operator_label("DEC", (2,)) == "DEC(address=[2])"


def test_graph_node_wraps_pet_object_state() -> None:
    obj = pet_object_from_int(60)

    node = PETGraphNode.from_object(obj)

    assert node.value == 60
    assert node.pet_object is obj
    assert node.to_dict()["value"] == 60
    assert node.to_dict()["object"]["value"] == 60


def test_operator_applications_by_value_only_returns_valid_applications() -> None:
    obj = pet_object_from_int(60)

    applications = operator_applications_by_value(obj)

    assert applications
    assert all(application.valid for application in applications)
    assert all(application.before_value == 60 for application in applications)
    assert all(application.after_object is not None for application in applications)


def test_operator_neighbors_by_value_for_60_contains_expected_edges() -> None:
    obj = pet_object_from_int(60)

    edges = operator_neighbors_by_value(obj)
    by_label = {edge.label: edge.target.value for edge in edges}

    assert by_label["NEW(parent_address=[],q=7)"] == 420
    assert by_label["DROP(parent_address=[],p=2)"] == 15
    assert by_label["DROP(parent_address=[],p=3)"] == 20
    assert by_label["DROP(parent_address=[],p=5)"] == 12
    assert by_label["NEW(parent_address=[2],q=3)"] == 960
    assert by_label["DROP(parent_address=[2],p=2)"] == 30
    assert by_label["INC(address=[2])"] == 120
    assert by_label["DEC(address=[2])"] == 30
    assert by_label["INC(address=[2, 2])"] == 240
    assert by_label["INC(address=[3])"] == 180
    assert by_label["INC(address=[5])"] == 300


def test_operator_neighbors_by_value_is_deterministic() -> None:
    obj = pet_object_from_int(60)

    first = [edge.to_dict() for edge in operator_neighbors_by_value(obj)]
    second = [edge.to_dict() for edge in operator_neighbors_by_value(obj)]

    assert first == second


def test_graph_edge_serializes_operator_application() -> None:
    obj = pet_object_from_int(60)

    edge = next(
        edge
        for edge in operator_neighbors_by_value(obj)
        if edge.label == "NEW(parent_address=[],q=7)"
    )

    assert isinstance(edge, PETGraphEdge)
    payload = edge.to_dict()

    assert payload["source_value"] == 60
    assert payload["target_value"] == 420
    assert payload["op"] == "NEW"
    assert payload["address"] == []
    assert payload["argument"] == 7
    assert payload["label"] == "NEW(parent_address=[],q=7)"
    assert payload["application"]["reason"] == "new-applied-by-value"

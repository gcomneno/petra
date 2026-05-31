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


def test_operator_neighbors_from_unit_root_can_start_generation() -> None:
    obj = pet_object_from_int(1)

    edges = operator_neighbors_by_value(obj)
    by_label = {edge.label: edge.target.value for edge in edges}

    assert by_label == {"NEW(parent_address=[],q=2)": 2}


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


def test_graph_path_records_values_labels_and_depth() -> None:
    from pet import PETGraphPath

    obj = pet_object_from_int(60)
    root_path = PETGraphPath.root(obj)
    edge = next(
        edge
        for edge in operator_neighbors_by_value(obj)
        if edge.label == "NEW(parent_address=[],q=7)"
    )

    path = root_path.extend(edge)

    assert root_path.depth == 0
    assert root_path.values == (60,)
    assert root_path.labels == ()

    assert path.depth == 1
    assert path.values == (60, 420)
    assert path.labels == ("NEW(parent_address=[],q=7)",)
    assert path.source.value == 60
    assert path.target.value == 420


def test_graph_path_rejects_non_contiguous_edge_extension() -> None:
    from pet import PETGraphPath

    root_60 = PETGraphPath.root(pet_object_from_int(60))
    edge_from_12 = operator_neighbors_by_value(pet_object_from_int(12))[0]

    import pytest

    with pytest.raises(ValueError, match="edge source does not match"):
        root_60.extend(edge_from_12)


def test_path_equivalence_uses_concrete_edge_identity() -> None:
    from pet import PETGraphPath, path_equivalent

    obj = pet_object_from_int(60)
    edge_new = next(
        edge
        for edge in operator_neighbors_by_value(obj)
        if edge.label == "NEW(parent_address=[],q=7)"
    )
    edge_drop = next(
        edge
        for edge in operator_neighbors_by_value(obj)
        if edge.label == "DROP(parent_address=[],p=5)"
    )

    left = PETGraphPath.root(obj).extend(edge_new)
    same = PETGraphPath.root(obj).extend(edge_new)
    different = PETGraphPath.root(obj).extend(edge_drop)

    assert path_equivalent(left, same)
    assert not path_equivalent(left, different)


def test_traverse_operator_graph_depth_zero_returns_root_path_only() -> None:
    from pet import traverse_operator_graph_by_value

    traversal = traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=0)

    assert traversal.root.value == 60
    assert traversal.max_depth == 0
    assert traversal.max_paths is None
    assert traversal.truncated is False
    assert traversal.path_count == 1
    assert traversal.paths[0].values == (60,)
    assert traversal.paths_at_depth(0) == traversal.paths
    assert traversal.paths_at_depth(1) == ()


def test_traverse_operator_graph_depth_one_records_neighbor_paths() -> None:
    from pet import traverse_operator_graph_by_value

    traversal = traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=1)
    by_label = {
        path.labels[0]: path.target.value for path in traversal.paths_at_depth(1)
    }

    assert traversal.truncated is False
    assert by_label["NEW(parent_address=[],q=7)"] == 420
    assert by_label["DROP(parent_address=[],p=5)"] == 12
    assert by_label["NEW(parent_address=[2],q=3)"] == 960
    assert by_label["INC(address=[2])"] == 120
    assert by_label["INC(address=[2, 2])"] == 240


def test_traverse_operator_graph_truncates_by_max_paths() -> None:
    from pet import traverse_operator_graph_by_value

    traversal = traverse_operator_graph_by_value(
        pet_object_from_int(60),
        max_depth=2,
        max_paths=5,
    )

    assert traversal.truncated is True
    assert traversal.path_count == 5
    assert traversal.paths[0].values == (60,)
    assert all(path.depth <= 2 for path in traversal.paths)


def test_traverse_operator_graph_is_deterministic_under_truncation() -> None:
    from pet import traverse_operator_graph_by_value

    first = traverse_operator_graph_by_value(
        pet_object_from_int(60),
        max_depth=2,
        max_paths=8,
    ).to_dict()
    second = traverse_operator_graph_by_value(
        pet_object_from_int(60),
        max_depth=2,
        max_paths=8,
    ).to_dict()

    assert first == second


def test_traverse_operator_graph_rejects_invalid_bounds() -> None:
    from pet import traverse_operator_graph_by_value

    import pytest

    with pytest.raises(ValueError, match="max_depth must be >= 0"):
        traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=-1)

    with pytest.raises(ValueError, match="max_paths must be >= 1"):
        traverse_operator_graph_by_value(
            pet_object_from_int(60),
            max_depth=1,
            max_paths=0,
        )

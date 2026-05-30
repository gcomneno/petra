from pet import (
    PETTrace,
    PETTraceStep,
    operator_neighbors_by_value,
    pet_object_from_int,
    trace_from_path,
    traverse_operator_graph_by_value,
)


def test_trace_from_root_path_has_no_steps() -> None:
    traversal = traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=0)

    trace = trace_from_path(traversal.paths[0])

    assert isinstance(trace, PETTrace)
    assert trace.root_value == 60
    assert trace.target_value == 60
    assert trace.depth == 0
    assert trace.values == (60,)
    assert trace.labels == ()
    assert trace.steps == ()
    assert trace.path_identity == ()


def test_trace_from_depth_one_path_records_step() -> None:
    traversal = traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=1)
    path = next(
        path
        for path in traversal.paths_at_depth(1)
        if path.labels == ("NEW(parent_address=[],q=7)",)
    )

    trace = trace_from_path(path)

    assert trace.root_value == 60
    assert trace.target_value == 420
    assert trace.depth == 1
    assert trace.values == (60, 420)
    assert trace.labels == ("NEW(parent_address=[],q=7)",)
    assert trace.path_identity == ((60, "NEW(parent_address=[],q=7)", 420),)

    step = trace.steps[0]
    assert isinstance(step, PETTraceStep)
    assert step.index == 1
    assert step.source_value == 60
    assert step.target_value == 420
    assert step.op == "NEW"
    assert step.address == ()
    assert step.argument == 7
    assert step.label == "NEW(parent_address=[],q=7)"
    assert step.application_reason == "new-applied-by-value"


def test_trace_from_depth_two_path_records_ordered_history() -> None:
    traversal = traverse_operator_graph_by_value(
        pet_object_from_int(60),
        max_depth=2,
        max_paths=30,
    )
    path = next(path for path in traversal.paths if path.depth == 2)

    trace = trace_from_path(path)

    assert trace.depth == 2
    assert len(trace.steps) == 2
    assert trace.values[0] == 60
    assert trace.values[-1] == trace.target_value
    assert trace.steps[0].index == 1
    assert trace.steps[1].index == 2
    assert trace.labels == path.labels
    assert trace.path_identity == path.identity_key()


def test_trace_serializes_root_and_steps() -> None:
    traversal = traverse_operator_graph_by_value(pet_object_from_int(60), max_depth=1)
    path = next(
        path
        for path in traversal.paths_at_depth(1)
        if path.labels == ("DROP(parent_address=[],p=5)",)
    )

    payload = trace_from_path(path).to_dict()

    assert payload["root_value"] == 60
    assert payload["target_value"] == 12
    assert payload["depth"] == 1
    assert payload["values"] == [60, 12]
    assert payload["labels"] == ["DROP(parent_address=[],p=5)"]
    assert payload["path_identity"] == [[60, "DROP(parent_address=[],p=5)", 12]]
    assert payload["steps"] == [
        {
            "index": 1,
            "source_value": 60,
            "target_value": 12,
            "op": "DROP",
            "address": [],
            "argument": 5,
            "label": "DROP(parent_address=[],p=5)",
            "application_reason": "drop-applied-by-value",
        }
    ]


def test_trace_from_manually_extended_neighbor_path_matches_edge() -> None:
    from pet import PETGraphPath

    obj = pet_object_from_int(60)
    edge = next(
        edge
        for edge in operator_neighbors_by_value(obj)
        if edge.label == "INC(address=[2])"
    )

    path = PETGraphPath.root(obj).extend(edge)
    trace = trace_from_path(path)

    assert trace.values == (60, 120)
    assert trace.steps[0].label == edge.label
    assert trace.steps[0].application_reason == edge.application.reason

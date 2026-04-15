from pet.rewrite_metric import build_graph, compose_transport_v1


def test_compose_transport_v1_exact_on_2_6_30() -> None:
    graph = build_graph(overscan=80)

    data = compose_transport_v1(graph, a=2, b=6, c=30)

    assert data["compatible"] is True
    assert data["result_reachable"] is True
    assert data["witness_cost"] == 2
    assert data["result_cost"] == 2
    assert data["witness_equals_result"] is True


def test_compose_transport_v1_witness_worse_on_2_3_4() -> None:
    graph = build_graph(overscan=80)

    data = compose_transport_v1(graph, a=2, b=3, c=4)

    assert data["compatible"] is True
    assert data["result_reachable"] is True
    assert data["witness_equals_result"] is False
    assert data["witness_cost"] is not None
    assert data["result_cost"] is not None
    assert data["witness_cost"] > data["result_cost"]

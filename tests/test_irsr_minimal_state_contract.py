import json
from pathlib import Path


def test_minimal_hostile_semiprime_state_contract():
    path = Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json")
    state = json.loads(path.read_text(encoding="utf-8"))

    assert set(state) == {"target", "skeleton", "slots", "coupling", "refinement"}

    assert "n" in state["target"]

    skeleton = state["skeleton"]
    assert skeleton["support_size"] == 2
    assert skeleton["exponent_profile"] == [1, 1]
    assert skeleton["squarefree"] is True
    assert skeleton["normalized_order"] == "a<=b"

    slots = state["slots"]
    assert isinstance(slots, list)
    assert len(slots) == 2
    assert [slot["slot"] for slot in slots] == ["a", "b"]

    for slot in slots:
        assert slot["kind"] == "prime"
        assert set(slot) == {"slot", "kind", "domain", "pet_hints"}

        domain = slot["domain"]
        assert set(domain) == {"type", "min", "max", "candidates"}
        assert domain["type"] == "range_or_candidates"
        assert isinstance(domain["candidates"], list)

        hints = slot["pet_hints"]
        assert set(hints) == {"near_generator", "block_shape"}
        assert isinstance(hints["near_generator"], list)
        assert isinstance(hints["block_shape"], list)

    coupling = state["coupling"]
    assert coupling["product_constraint"] == "a*b=n"
    assert isinstance(coupling["joint_pet_constraints"], list)
    assert isinstance(coupling["forbidden_patterns"], list)

    refinement = state["refinement"]
    assert refinement["iteration"] == 0
    assert refinement["status"] == "open"
    assert refinement["payload_ready"] is False

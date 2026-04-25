from __future__ import annotations

from pet.builder_from_irsr import _generate_structural_profile_candidates_v1


def _normalize(specs: list[dict]) -> list[tuple]:
    rows = []
    for spec in specs:
        rows.append(
            (
                spec["backend"],
                tuple(spec.get("exponent_profile", [])),
                spec.get("support_size"),
                spec["radius"],
            )
        )
    return rows


def test_structural_profile_search_space_v1_reproduces_current_profiles() -> None:
    specs = _generate_structural_profile_candidates_v1()

    assert _normalize(specs) == [
        ("generic-exponent", (2,), None, 16),
        ("generic-exponent", (2, 1), None, 16),
        ("generic-squarefree", (), 3, 16),
        ("generic-squarefree", (), 4, 16),
        ("generic-squarefree", (), 5, 64),
    ]


def test_structural_profile_search_space_v1_excludes_out_of_scope_profiles() -> None:
    specs = _generate_structural_profile_candidates_v1()
    normalized = _normalize(specs)

    assert ("generic-exponent", (3,), None, 1) not in normalized
    assert ("generic-exponent", (1, 1), None, 1) not in normalized
    assert ("generic-squarefree", (), 2, 16) not in normalized
    assert ("generic-squarefree", (), 6, 64) not in normalized

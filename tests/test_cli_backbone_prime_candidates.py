from pet.cli import _iter_backbone_prime_candidates


def test_iter_backbone_prime_candidates_yields_pet_backbone_generators():
    assert list(_iter_backbone_prime_candidates(30)) == [
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
    ]


def test_iter_backbone_prime_candidates_handles_limits_below_two():
    assert list(_iter_backbone_prime_candidates(1)) == []

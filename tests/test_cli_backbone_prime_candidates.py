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


def test_iter_backbone_prime_window_candidates_yields_windowed_generators():
    from pet.cli import _iter_backbone_prime_window_candidates

    assert list(_iter_backbone_prime_window_candidates(10, 30)) == [
        11,
        13,
        17,
        19,
        23,
        29,
    ]


def test_iter_backbone_prime_window_candidates_handles_empty_window():
    from pet.cli import _iter_backbone_prime_window_candidates

    assert list(_iter_backbone_prime_window_candidates(1011, 1012)) == []


def test_iter_scanned_prime_window_candidates_scans_only_window():
    from pet.cli import _iter_scanned_prime_window_candidates

    assert list(_iter_scanned_prime_window_candidates(100, 110)) == [
        101,
        103,
        107,
        109,
    ]

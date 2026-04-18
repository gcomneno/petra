import json

from pet.cli import _parse_factor_spec_file


def test_parse_factor_spec_can_skip_prime_validation_when_trusted(tmp_path):
    spec = {
        "trust_primes": True,
        "factors": [
            [2, 1],
            [3, 1],
            [5, 1],
            [7, 1],
            [11, 1],
            [13, 1],
        ],
    }

    path = tmp_path / "trusted.json"
    path.write_text(json.dumps(spec), encoding="utf-8")

    assert _parse_factor_spec_file(str(path)) == (
        (2, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (11, 1),
        (13, 1),
    )

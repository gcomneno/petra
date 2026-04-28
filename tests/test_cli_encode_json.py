#!/usr/bin/env python3
import json
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (
            2,
            [
                {"p": 2, "e": None},
            ],
        ),
        (
            12,
            [
                {"p": 2, "e": [{"p": 2, "e": None}]},
                {"p": 3, "e": None},
            ],
        ),
        (
            72,
            [
                {"p": 2, "e": [{"p": 3, "e": None}]},
                {"p": 3, "e": [{"p": 2, "e": None}]},
            ],
        ),
    ],
)
def test_cli_encode_json_matches_spec_examples(n, expected):
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "encode", "--json", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    assert data == expected

#!/usr/bin/env python3
import json
import subprocess
import sys


PET_72 = [
    {"p": 2, "e": [{"p": 3, "e": None}]},
    {"p": 3, "e": [{"p": 2, "e": None}]},
]


def test_cli_decode_json_file(tmp_path):
    pet_file = tmp_path / "pet-72.json"
    pet_file.write_text(json.dumps(PET_72))

    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "decode", str(pet_file)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == "72"


def test_cli_validate_json_file(tmp_path):
    pet_file = tmp_path / "pet-72.json"
    pet_file.write_text(json.dumps(PET_72))

    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "validate", str(pet_file)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == "OK"


def test_cli_render_json_file(tmp_path):
    pet_file = tmp_path / "pet-72.json"
    pet_file.write_text(json.dumps(PET_72))

    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "render", str(pet_file)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "(2," in result.stdout
    assert "(3," in result.stdout
    assert "•" in result.stdout

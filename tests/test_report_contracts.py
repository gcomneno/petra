from pathlib import Path
import re

import pytest


REPORT_CONTRACTS = {
    "docs/reports/generated/metrics-2-10000.md": {
        "kind": "scan-backed",
    },
    "docs/reports/generated/atlas-2-100000.md": {
        "kind": "scan+summary-backed",
    },
    "docs/reports/generated/atlas-2-1000000.md": {
        "kind": "scan+summary-backed",
    },
    "docs/reports/generated/families-benchmark-disjoint.md": {
        "kind": "script-backed-benchmark",
    },
    "docs/reports/generated/signatures-catalog-2-1000000.md": {
        "kind": "scan-backed",
    },
}

EXISTING_REPORT_CONTRACTS = {
    path: spec for path, spec in REPORT_CONTRACTS.items() if Path(path).exists()
}



def read_text(path: str) -> str:
    file_path = Path(path)
    assert file_path.exists(), f"Expected report file to exist: {path}"
    return file_path.read_text(encoding="utf-8")


def assert_common_report_markers(text: str, path: str) -> None:
    assert "## Scope" in text, f"{path}: missing '## Scope' section"
    assert "## Observations" in text, f"{path}: missing '## Observations' section"

    has_limits = "## Interpretation and limits" in text or "## Limits" in text
    assert has_limits, f"{path}: missing limits/interpretation section"


def assert_scan_backed_markers(text: str, path: str) -> None:
    assert (
        "python3 -m src.pet.cli scan" in text
    ), f"{path}: missing scan reproduction command"

    assert (
        "docs/reports/data/scan-" in text
    ), f"{path}: missing explicit scan dataset path"

    has_bounded_range = bool(
        re.search(r"\b\d+\.\.\d+\b", text) or re.search(r"\b\d+\s+to\s+\d+\b", text)
    )
    assert has_bounded_range, f"{path}: missing explicit bounded range marker"


def assert_summary_backed_markers(text: str, path: str) -> None:
    assert (
        "tools/atlas_summary.py" in text
    ), f"{path}: missing atlas summary helper reference"

    assert (
        "atlas-summary-" in text
    ), f"{path}: missing derived atlas summary artifact reference"


def assert_script_benchmark_markers(text: str, path: str) -> None:
    assert "## Method" in text, f"{path}: missing '## Method' section"

    assert (
        "pet families benchmark-disjoint" in text
        or "tools/cluster_families_disjoint.py" in text
    ), f"{path}: missing benchmark command/script reference"


@pytest.mark.parametrize("path,spec", EXISTING_REPORT_CONTRACTS.items())
def test_canonical_bounded_reports_expose_minimum_contract(path: str, spec: dict) -> None:
    text = read_text(path)

    assert_common_report_markers(text, path)

    kind = spec["kind"]

    if kind == "scan-backed":
        assert_scan_backed_markers(text, path)
    elif kind == "scan+summary-backed":
        assert_scan_backed_markers(text, path)
        assert_summary_backed_markers(text, path)
    elif kind == "script-backed-benchmark":
        assert_script_benchmark_markers(text, path)
    else:
        raise AssertionError(f"{path}: unsupported report contract kind: {kind}")

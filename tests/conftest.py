"""Pytest configuration for the PETRA test suite."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register the marker declared in pyproject.toml."""

    config.addinivalue_line(
        "markers",
        "legacy: historical PET test (kept for compatibility)",
    )

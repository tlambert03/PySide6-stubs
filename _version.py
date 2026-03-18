"""Resolve the target PySide6 version (used by hatch version source)."""

from __future__ import annotations

import os
from pathlib import Path

import httpx

PYPI_URL = "https://pypi.org/pypi/PySide6/json"
VERSION_FILE = Path(__file__).parent / ".pyside6-version"


def get_pyside6_version() -> str:
    """Resolve target version: env var > .pyside6-version file > PyPI latest."""
    if version := os.environ.get("PYSIDE6_VERSION"):
        return version.lstrip("v")

    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()

    resp = httpx.get(PYPI_URL)
    resp.raise_for_status()
    return resp.json()["info"]["version"]

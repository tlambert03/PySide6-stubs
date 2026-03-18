"""Resolve the target PySide6 version (used by hatch version source)."""

from __future__ import annotations

import os
import subprocess

import httpx

PYPI_URL = "https://pypi.org/pypi/PySide6/json"


def get_pyside6_version() -> str:
    """Resolve target version: PYSIDE6_VERSION env var > git tag > PyPI latest."""
    if version := os.environ.get("PYSIDE6_VERSION"):
        return version.lstrip("v")

    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--exact-match"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return tag.lstrip("v")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    resp = httpx.get(PYPI_URL)
    resp.raise_for_status()
    return resp.json()["info"]["version"]

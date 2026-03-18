"""Custom hatch build hook to extract PySide6 stubs from the official wheel."""

from __future__ import annotations

import io
import os
import re
import subprocess
import zipfile
from pathlib import Path

import httpx
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

STUBS_DIR = Path(__file__).parent / "PySide6-stubs"
PYPI_URL = "https://pypi.org/pypi/PySide6"


def _resolve_version() -> str:
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

    resp = httpx.get(f"{PYPI_URL}/json")
    resp.raise_for_status()
    return resp.json()["info"]["version"]


def _find_wheel_url(version: str) -> str:
    """Find any PySide6 wheel URL for the given version."""
    resp = httpx.get(f"{PYPI_URL}/{version}/json")
    resp.raise_for_status()
    releases = resp.json()["urls"]

    for release in releases:
        if release["filename"].endswith(".whl"):
            return release["url"]

    raise RuntimeError(f"No wheel found for PySide6 {version}")


def _extract_stubs(wheel_bytes: bytes, dest: Path) -> None:
    """Extract .pyi files from a PySide6 wheel into dest directory."""
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as zf:
        for name in zf.namelist():
            if re.match(r"^PySide6/[^/]+\.pyi$", name):
                stub_name = name.split("/", 1)[1]
                (dest / stub_name).write_bytes(zf.read(name))


def _ensure_stubs() -> str:
    """Download and extract stubs if not already present. Return version."""
    version = _resolve_version()

    marker = STUBS_DIR / ".version"
    if marker.exists() and marker.read_text().strip() == version:
        return version

    # Clean old stubs
    if STUBS_DIR.exists():
        for f in STUBS_DIR.iterdir():
            f.unlink()
    else:
        STUBS_DIR.mkdir()

    wheel_url = _find_wheel_url(version)
    print(f"Downloading PySide6 {version} wheel to extract stubs...")
    wheel_resp = httpx.get(wheel_url, follow_redirects=True, timeout=300)
    wheel_resp.raise_for_status()

    _extract_stubs(wheel_resp.content, STUBS_DIR)

    # Write __init__.pyi for PEP 561
    init_pyi = STUBS_DIR / "__init__.pyi"
    if not init_pyi.exists():
        init_pyi.write_text("")

    # Write py.typed marker
    (STUBS_DIR / "py.typed").write_text("")

    # Write version marker
    marker.write_text(version)

    stub_count = len(list(STUBS_DIR.glob("*.pyi")))
    print(f"Extracted {stub_count} stub files for PySide6 {version}")
    return version


class CustomBuildHook(BuildHookInterface):
    """Hatch build hook that fetches PySide6 stubs before building."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict) -> None:
        _ensure_stubs()
        build_data["force_include"][str(STUBS_DIR)] = "PySide6-stubs"

# PySide6-stubs

PySide6 type stubs as a standalone, lightweight package — without installing
PySide6 itself.

> **Note:** This package is not intended to be published to PyPI. It is
> intended for development and type checking only.  Install it
> directly from GitHub (see [Usage](#usage) below).

## Why?

Libraries that support both PyQt6 and PySide6 need to pick one package for
static type checking. The standard pattern is:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
else:
    # runtime: use whichever backend is installed
    from PyQt6.QtWidgets import QWidget
```

Type checkers only see the `TYPE_CHECKING` branch, so they need the stubs from
PySide6 to resolve types — even if the library (or its users) run PyQt6 at
runtime.

PySide6 ships excellent stubs, but installing it pulls in ~200 MB of compiled Qt
binaries that are completely unnecessary for type checking. This package extracts
just the `.pyi` stub files and installs them as a PEP 561 stub package.

## Usage

Add it as a dev dependency pointing at a specific version tag:

```bash
uv add --dev "PySide6-stubs @ git+https://github.com/tlambert03/PySide6-stubs@v6.8.0"
```

This adds the following to your `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "PySide6-stubs @ git+https://github.com/tlambert03/PySide6-stubs@v6.8.0",
]
```

Then run your type checker as usual:

```bash
uv run pyright
```

### Picking a version

Tag the version to the **lowest PySide6 release you intend to support**.
Available tags correspond to PySide6 releases on PyPI (e.g. `v6.7.0`, `v6.8.0`,
`v6.10.2`).

## How it works

At build time, the package:

1. Resolves a target PySide6 version (git tag → PyPI latest)
2. Downloads the official PySide6 wheel from PyPI
3. Extracts all `.pyi` stub files
4. Packages them as `PySide6-stubs` with a matching version

No PySide6 runtime code is included — just stubs.

### Version resolution order

| Priority | Source | Example |
|----------|--------|---------|
| 1 | `PYSIDE6_VERSION` env var | `PYSIDE6_VERSION=6.8.0 pip install .` |
| 2 | Git tag | `pip install 'PySide6-stubs @ git+...@v6.8.0'` |
| 3 | PyPI latest | `pip install .` |

## Building locally

```bash
# latest
uv build --wheel

# specific version
PYSIDE6_VERSION=6.8.0 uv build --wheel
```

# Qt-stubs

Qt for python type stubs as a standalone, lightweight package — without installing
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
    from PySide6.QtWidgets import QWidget, QApplication
else:
    try:
        from PyQt6.QtWidgets import QWidget, QApplication
    except ImportError:
        from PySide6.QtWidgets import QWidget, QApplication
    # or qtpy ... works too.  And typing will still be slightly better.
    # though some naming/imports might be slightly different from qtpy.
```

Type checkers only see the `TYPE_CHECKING` branch, so they need the stubs from
PySide6 to resolve types — even if the library (or its users) run PyQt6 at
runtime.

PySide6 ships excellent stubs, but installing it pulls in ~200 MB of compiled Qt
binaries that are completely unnecessary for type checking. This package extracts
just the `.pyi` stub files and installs them as a PEP 561 stub package.

## Usage

Add it as a dev dependency pointing at a specific version tag (usually, the
lowest Qt version you intend to support):

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

Pick the **lowest Qt API you intend to support**. Available tags
correspond to every stable PySide6 release on PyPI (e.g. `v6.7.0`, `v6.8.0`,
`v6.10.2`). This ensures your type checker won't see APIs that don't exist in
your minimum supported version.

## How it works

The repo itself contains no stub files. Each git tag (e.g. `v6.8.0`) points to
a commit with a `.pyside6-version` file containing that version number. When
you install with `@v6.8.0` in the URL, pip/uv checks out that tag and runs the
build, which:

1. Reads the version from `.pyside6-version` (in this case `6.8.0`)
2. Downloads the official PySide6 6.8.0 wheel from PyPI
3. Extracts all `.pyi` stub files
4. Packages them as `PySide6-stubs` version `6.8.0`

No PySide6 runtime code is included — just stubs.

You can also override the version with an environment variable:

```bash
PYSIDE6_VERSION=6.9.0 uv build --wheel
```

If neither `.pyside6-version` nor the env var is set, it falls back to the
latest PySide6 release on PyPI.

## How is this different from `python-qt-tools/PySide6-stubs`?

[`PySide6-stubs` on PyPI](https://pypi.org/project/PySide6-stubs/) (from
[python-qt-tools](https://github.com/python-qt-tools/PySide6-stubs)) is a
separate project that extracts the official stubs and then layers on **manual
corrections** — fixing nullable parameters, optional return types, signal
method signatures, and other inaccuracies in the upstream stubs.
However, it only updates periodically and APIs are not guaranteed to match
any specific PySide6 release.

This repo does something different: it extracts the **unmodified** official
stubs from a specific PySide6 release *at install time* and repackages them.
No corrections are applied.

| | `python-qt-tools/PySide6-stubs` | This repo |
|---|---|---|
| Published on PyPI | Yes | No (git-only) |
| Stub source | Official + manual fixes | Official, unmodified |
| Version coverage | Lags behind (latest: 6.7.3) | Every stable release |
| Install size | Stubs only | Stubs only |
| Use case | Best-effort accuracy | Version-pinned, zero-overhead stubs |

## Building locally

```bash
# latest
uv build --wheel

# specific version
PYSIDE6_VERSION=6.8.0 uv build --wheel
```

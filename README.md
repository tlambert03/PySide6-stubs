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

<details>

<summary>Stubs comparison</summary>

1. nullability

    PyQt6 marks nearly everything as `Optional`. This includes parameters that should never be None:

    ```python
    # PyQt6 — wrong: you can't setText(None) in C++ Qt
    def setText(self, text: typing.Optional[str]) -> None: ...
    def setWindowTitle(self, a0: typing.Optional[str]) -> None: ...
    def addWidget(self, w: typing.Optional[QWidget]) -> None: ...
    
    # PySide6 — correct: str is required
    def setText(self, text: str, /) -> None: ...
    def setWindowTitle(self, title: str, /) -> None: ...
    def addWidget(self, arg__1: PySide6.QtWidgets.QWidget, /) -> None: ...
    ```

    PyQt6's SIP generator appears to blanket-mark pointer/reference parameters as Optional, which is technically "safe" but destroys the value of type checking —
    you'll never get a warning for passing None where it would segfault.

1. Implicit conversions

    PySide6 encodes Qt's implicit C++ conversions as unions:

    ```python
    # PySide6 — knows QPixmap is implicitly convertible to QIcon
    def setIcon(self, icon: QIcon | QPixmap, /) -> None: ...
    def setPixmap(self, pixmap: QPixmap | QImage, /) -> None: ...
    def setBrush(self, brush: QBrush | Qt.BrushStyle | Qt.GlobalColor | QColor | QGradient | QImage | QPixmap, /) -> None: ...
    
    # PyQt6 — only accepts the exact type
    def setIcon(self, icon: QIcon) -> None: ...
    def setPixmap(self, pixmap: QPixmap) -> None: ...
    ```

    `label.setPixmap(QImage(...))` is valid Qt code and works at runtime with both backends,
    but PyQt6's stubs would flag it as an error.

1. Positional-only parameters (/)

    PySide6 uses the / marker on most signatures. PyQt6 uses it on zero.
    This correctly prevents `widget.setText(text="hello")` which would fail at runtime (C++
    bindings don't support keyword arguments for most positional params).

1. Keyword-only property arguments in `__init__`

    Both backends support setting Qt properties as keyword arguments in
    constructors at runtime (e.g. `QPushButton(text="Click", flat=True)`).
    PySide6's stubs model this; PyQt6's don't — so pyright/mypy will reject
    valid code when using PyQt6 stubs:

1. Enum values have actual int values

    ```python
    # PySide6 — actual values
    DrawWindowBackground = 0x1
    DrawChildren = 0x2
    
    # PyQt6 — opaque
    DrawWindowBackground = ... # type: QWidget.RenderFlag
    DrawChildren = ... # type: QWidget.RenderFlag
    ```

</details>

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

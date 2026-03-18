# PySide6-stubs

## Project overview

This repo repackages the official PySide6 `.pyi` stub files as a standalone
PEP 561 stub package, without the ~200 MB of Qt binaries. It is never published
to PyPI — users install directly from GitHub at a specific git tag.

## Architecture

- `_version.py` — version resolution for hatch's dynamic version source
- `hatch_build.py` — custom hatch build hook that downloads a PySide6 wheel
  from PyPI and extracts `.pyi` files at build time
- `.pyside6-version` — single-line file containing the target version; differs
  per git tag (this is how the `@v6.8.0` in the install URL selects the version)
- `PySide6-stubs/` — generated at build time, gitignored

## How version tagging works

Every stable PySide6 release on PyPI has a corresponding git tag in this repo.
Each tag points to a unique commit whose only difference is the content of
`.pyside6-version`. The build hook reads this file to know which PySide6 wheel
to download.

## Regenerating all tags

When `hatch_build.py`, `_version.py`, `pyproject.toml`, or any other build
file changes, ALL tags must be recreated so they include the updated code.

```bash
# 1. Commit your changes to main
git add -A && git commit -m "describe your change"

# 2. Delete all remote tags
git push origin --delete $(git tag -l)

# 3. Delete all local tags
git tag -l | xargs git tag -d

# 4. Regenerate one commit+tag per stable PySide6 release
python3 -c "
import urllib.request, json
from packaging.version import Version
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/PySide6/json').read())
for v, files in data['releases'].items():
    pv = Version(v)
    if pv.is_prerelease or pv.is_devrelease:
        continue
    if any(f['filename'].endswith('.whl') for f in files):
        print(v)
" | sort -V | while read v; do
    echo "$v" > .pyside6-version
    git add .pyside6-version
    git commit -m "v$v" -q
    git tag "v$v"
done

# 5. Force-push main (history is rewritten) and push all tags
git push origin main --force --tags
```

**Important:** This force-pushes main because the per-version commits are
rebased on top of the latest changes. Users installing from a tag are
unaffected — their lockfile pins a specific tag ref.

## Testing

```bash
# Build for a specific version
PYSIDE6_VERSION=6.8.0 uv build --wheel

# Build from a tag
git checkout v6.8.0 && uv build --wheel

# Verify wheel contents
unzip -l dist/pyside6_stubs-*.whl | head -20
```

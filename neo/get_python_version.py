#!/usr/bin/env python3
"""
Detect required Python major.minor for this repo.

Priority:
1) pyproject.toml -> [project].requires-python (if present)
2) .python-version (if present)
3) modules/launch_utils.py -> check_python_version() AST parse

Input:
- Environment variable: REFORGE_PATH (repo root)
- Optional CLI argument: -strip (or --strip) to remove period from output

Output:
- Prints major.minor (e.g. 3.13) to stdout by default
- With -strip/--strip, prints without period (e.g. 313)
- Exits non-zero on failure
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path


def _first_major_minor(text: str) -> str | None:
    m = re.search(r"(\d+)\.(\d+)", text)
    if not m:
        return None
    return f"{m.group(1)}.{m.group(2)}"


def _from_pyproject(root: Path) -> str | None:
    p = root / "pyproject.toml"
    if not p.is_file():
        return None

    data = p.read_text(encoding="utf-8", errors="replace")

    # Try stdlib tomllib first (py3.11+)
    try:
        import tomllib  # type: ignore

        obj = tomllib.loads(data)
        spec = (obj.get("project") or {}).get("requires-python")
        if isinstance(spec, str):
            return _first_major_minor(spec)
    except Exception:
        pass

    # Fallback regex scan
    m = re.search(r"(?m)^\s*requires-python\s*=\s*['\"]([^'\"]+)['\"]\s*$", data)
    if m:
        return _first_major_minor(m.group(1))

    return None


def _from_python_version_file(root: Path) -> str | None:
    p = root / ".python-version"
    if not p.is_file():
        return None

    raw = p.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return None

    # Accept forms like "3.13" or "3.13.12"
    return _first_major_minor(raw)


def _from_launch_utils(root: Path) -> str | None:
    p = root / "modules" / "launch_utils.py"
    if not p.is_file():
        return None

    src = p.read_text(encoding="utf-8", errors="replace")

    try:
        mod = ast.parse(src)
    except SyntaxError:
        return None

    fn = None
    for node in mod.body:
        if isinstance(node, ast.FunctionDef) and node.name == "check_python_version":
            fn = node
            break
    if fn is None:
        return None

    major = None
    minor = None

    for n in ast.walk(fn):
        # Pattern used in this repo: if not (major == 3 and minor == 13):
        if (
            isinstance(n, ast.Compare)
            and len(n.ops) == 1
            and isinstance(n.ops[0], ast.Eq)
        ):
            if (
                isinstance(n.left, ast.Name)
                and len(n.comparators) == 1
                and isinstance(n.comparators[0], ast.Constant)
            ):
                val = n.comparators[0].value
                if isinstance(val, int):
                    if n.left.id == "major":
                        major = val
                    elif n.left.id == "minor":
                        minor = val

    if isinstance(major, int) and isinstance(minor, int):
        return f"{major}.{minor}"

    return None


def main() -> int:
    strip_output = False
    for arg in sys.argv[1:]:
        if arg in ("-strip", "--strip"):
            strip_output = True
        else:
            print(f"ERROR: Unknown argument: {arg}", file=sys.stderr)
            print("Usage: get_python_version.py [-strip]", file=sys.stderr)
            return 2

    root_env = os.environ.get("REFORGE_PATH", "").strip()
    if not root_env:
        print("ERROR: REFORGE_PATH is not set", file=sys.stderr)
        return 2

    root = Path(root_env).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"ERROR: REFORGE_PATH is not a directory: {root}", file=sys.stderr)
        return 2

    for detector in (_from_pyproject, _from_python_version_file, _from_launch_utils):
        ver = detector(root)
        if ver:
            print(ver.replace(".", "") if strip_output else ver)
            return 0

    print(
        "ERROR: Could not determine required Python version from repository contents",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

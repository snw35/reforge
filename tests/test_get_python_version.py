"""Tests for neo/get_python_version.py.

The detector drives both `uv python install` and the sageattention wheel tag in
neo/Dockerfile, so a shape it cannot parse silently produced an impossible wheel
filename (see the scheduled-actions failure of run 42514819472).
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "neo" / "get_python_version.py"

_spec = importlib.util.spec_from_file_location("get_python_version", SCRIPT)
assert _spec is not None and _spec.loader is not None
gpv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gpv)


def _launch_utils(body: str) -> str:
    return (
        "import sys\n"
        "\n"
        "\n"
        "def check_python_version():\n"
        "    major = sys.version_info.major\n"
        "    minor = sys.version_info.minor\n"
        "    micro = sys.version_info.micro\n"
        "\n"
        f"{body}"
    )


class DetectorCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, relpath: str, content: str) -> None:
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.dict("os.environ", {"REFORGE_PATH": str(self.root)}):
            with mock.patch.object(sys, "argv", ["get_python_version.py", *args]):
                with redirect_stdout(out), redirect_stderr(io.StringIO()):
                    code = gpv.main()
        return code, out.getvalue().strip()


class TestLaunchUtilsAst(DetectorCase):
    def test_equality_form(self) -> None:
        # forge 2.30: if not (major == 3 and minor == 13)
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    if not (major == 3 and minor == 13):\n"
                "        raise RuntimeError('unsupported')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.13"))
        self.assertEqual(self.run_main("-strip"), (0, "313"))

    def test_less_than_form(self) -> None:
        # forge 2.31: if minor < 13  ->  3.13 or newer is required
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    if minor < 13:\n        raise RuntimeError('unsupported')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.13"))
        self.assertEqual(self.run_main("--strip"), (0, "313"))

    def test_less_than_or_equal_form(self) -> None:
        # if minor <= 12 is the same requirement expressed on the failure branch
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    if minor <= 12:\n        raise RuntimeError('unsupported')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.13"))

    def test_both_forms_present_takes_highest(self) -> None:
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    if not (major == 3 and minor == 12):\n"
                "        raise RuntimeError('unsupported')\n"
                "    if minor < 13:\n"
                "        raise RuntimeError('unsupported')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.13"))


class TestOtherSources(DetectorCase):
    def test_pyproject(self) -> None:
        self.write("pyproject.toml", '[project]\nrequires-python = ">=3.12"\n')
        self.assertEqual(self.run_main(), (0, "3.12"))

    def test_python_version_file(self) -> None:
        self.write(".python-version", "3.11.9\n")
        self.assertEqual(self.run_main(), (0, "3.11"))

    def test_pyproject_wins_over_launch_utils(self) -> None:
        self.write("pyproject.toml", '[project]\nrequires-python = ">=3.12"\n')
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    if minor < 13:\n        raise RuntimeError('unsupported')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.12"))

    def test_tested_with_message_fallback(self) -> None:
        # No usable comparison, but the human-readable message carries the version
        self.write(
            "modules/launch_utils.py",
            _launch_utils(
                "    raise RuntimeError('this program is tested with 3.13.15 Python')\n"
            ),
        )
        self.assertEqual(self.run_main(), (0, "3.13"))


class TestFailures(DetectorCase):
    def test_unknown_layout_fails_loudly(self) -> None:
        self.write("modules/launch_utils.py", _launch_utils("    return None\n"))
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(out, "")

    def test_missing_reforge_path(self) -> None:
        out = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch.object(sys, "argv", ["get_python_version.py"]):
                with redirect_stdout(out), redirect_stderr(io.StringIO()):
                    code = gpv.main()
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")

    def test_unknown_argument(self) -> None:
        code, out = self.run_main("--bogus")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()

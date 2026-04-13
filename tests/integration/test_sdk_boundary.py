"""SDK boundary integration tests (§4)."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUI_ROOT = REPO_ROOT / "src" / "drone_rl" / "gui"
TESTS_ROOT = REPO_ROOT / "tests"
SDK_TEST_ROOT = TESTS_ROOT / "unit" / "test_sdk"
INTEGRATION_ROOT = TESTS_ROOT / "integration"


def _iter_import_from_modules(py_file: Path) -> list[str]:
    tree = ast.parse(py_file.read_text())
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_gui_never_imports_rl_directly() -> None:
    """GUI modules must not import from drone_rl.rl directly."""
    offenders: list[Path] = []
    for py_file in GUI_ROOT.rglob("*.py"):
        modules = _iter_import_from_modules(py_file)
        if any(m.startswith("drone_rl.rl") for m in modules):
            offenders.append(py_file)
    assert offenders == []


def test_non_sdk_integration_tests_do_not_import_rl_directly() -> None:
    """Integration tests outside SDK boundary checks avoid direct RL imports."""
    offenders: list[Path] = []
    for py_file in INTEGRATION_ROOT.rglob("*.py"):
        if SDK_TEST_ROOT in py_file.parents:
            continue
        modules = _iter_import_from_modules(py_file)
        if any(m.startswith("drone_rl.rl") for m in modules):
            offenders.append(py_file)
    assert offenders == []

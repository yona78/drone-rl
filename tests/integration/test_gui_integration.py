"""
Integration tests — GUI boundary enforcement (§4, §6).

Verifies that no file under src/drone_rl/gui/ imports directly from
drone_rl.rl, and that all GUI source files are within the line limit.

Reference: CODE_PLAN Phase 5, §5.8.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

GUI_DIR = Path(__file__).resolve().parents[2] / "src" / "drone_rl" / "gui"
SRC_DIR = Path(__file__).resolve().parents[2] / "src"

_TKINTER_AVAILABLE = importlib.util.find_spec("tkinter") is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _gui_python_files() -> list[Path]:
    return list(GUI_DIR.rglob("*.py"))


def _rl_imports_in_file(path: Path) -> list[str]:
    """Return any AST-level imports that reference the rl sub-package."""
    tree = ast.parse(path.read_text())
    violations: list[str] = []
    for node in ast.walk(tree):
        # absolute: from drone_rl.rl...  /  import drone_rl.rl...
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("drone_rl.rl"):
                    violations.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # absolute form
            if module.startswith("drone_rl.rl"):
                violations.append(f"from {module}")
            # relative form: level > 0 means relative; module == "rl" or
            # starts with "rl." means from ..rl or from ..rl.something
            if node.level > 0 and (module == "rl" or module.startswith("rl.")):
                violations.append(f"from {'.' * node.level}{module}")
    return violations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_gui_does_not_import_rl_directly() -> None:
    """No GUI file may import from drone_rl.rl.* (§4 SDK boundary)."""
    all_violations: list[str] = []
    for py_file in _gui_python_files():
        hits = _rl_imports_in_file(py_file)
        for h in hits:
            all_violations.append(f"{py_file.name}: {h}")
    assert all_violations == [], "SDK boundary violated:\n" + "\n".join(all_violations)


def test_all_gui_files_exist() -> None:
    """Core GUI module files must be present on disk."""
    required = [
        "app.py",
        "app_ui_mixin.py",
        "app_menu.py",
        "canvas.py",
        "canvas_overlays.py",
        "canvas_editing.py",
        "editor.py",
        "charts.py",
        "panels.py",
        "hyperparameter_panel.py",
        "playback_controls.py",
        "io_panel.py",
    ]
    missing = [f for f in required if not (GUI_DIR / f).exists()]
    assert missing == [], f"Missing GUI files: {missing}"


@pytest.mark.skipif(
    not _TKINTER_AVAILABLE,
    reason="tkinter not available in this environment",
)
def test_gui_modules_import_cleanly() -> None:
    """All GUI modules must be importable without raising errors."""
    sys.path.insert(0, str(SRC_DIR))
    import matplotlib

    matplotlib.use("Agg")
    modules = [
        "drone_rl.gui.app",
        "drone_rl.gui.app_ui_mixin",
        "drone_rl.gui.app_menu",
        "drone_rl.gui.canvas",
        "drone_rl.gui.canvas_overlays",
        "drone_rl.gui.canvas_editing",
        "drone_rl.gui.editor",
        "drone_rl.gui.panels",
        "drone_rl.gui.hyperparameter_panel",
        "drone_rl.gui.playback_controls",
        "drone_rl.gui.io_panel",
    ]
    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
        except ImportError as exc:
            pytest.fail(f"{mod_name} failed to import: {exc}")


def test_gui_line_counts_within_limit() -> None:
    """Every GUI source file must be ≤150 lines."""
    violations = []
    for f in _gui_python_files():
        lines = len(f.read_text().splitlines())
        if lines > 150:
            violations.append(f"{f.name}: {lines} lines")
    assert violations == [], "Files exceed 150-line limit:\n" + "\n".join(violations)

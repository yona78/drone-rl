"""
EnvironmentEditor — mouse-driven grid cell editor (Phase 5).

Standalone editor widget reusing GridCanvas logic.
Never imports from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §3.2.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ..types.grid import GridState
from .canvas import GridCanvas


class EnvironmentEditor(GridCanvas):
    """
    Interactive grid editor wrapper around GridCanvas.

    Inherits all drawing, editing, and binding logic from GridCanvas.
    Used primarily in Toplevel configuration windows.
    """

    def __init__(
        self,
        parent: tk.Widget,
        grid: GridState,
        cell_size: int = 50,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        # Initialise base GridCanvas; it handles width/height and bindings
        super().__init__(parent, grid, cell_size, on_change)
        # Force redraw to ensure Start/Goal labels appear immediately
        self.draw_grid()

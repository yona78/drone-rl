"""
GridCanvas — tkinter canvas renderer for the RL grid (Phase 5).

Draws cells, agent, path, directional policy arrows, and a persistent
color legend. Supports interactive cell editing via CanvasEditingMixin.
Never imports from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §3.2.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ..constants import CELL_COLORS
from ..types.grid import GridState
from .canvas_editing import CanvasEditingMixin
from .canvas_overlays import CanvasOverlayMixin


class GridCanvas(tk.Canvas, CanvasOverlayMixin, CanvasEditingMixin):
    """
    Canvas that renders the Q-Learning grid and agent overlays.

    **Input Data:** GridState, cell_size (pixels).
    **Output Data:** Drawn tkinter canvas items.
    **Setup Data:** Configured from GridState dimensions on init.
    """

    _AGENT_TAG = "agent"
    _PATH_TAG = "path"
    _ARROW_TAG = "arrows"

    def __init__(
        self,
        parent: tk.Widget,
        grid: GridState,
        cell_size: int = 50,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self._grid = grid
        self._cs = cell_size
        self._on_change = on_change
        w = grid.cols * cell_size + 120  # +120 for legend
        h = grid.rows * cell_size + 2
        super().__init__(parent, width=w, height=h, bg="white", cursor="crosshair")
        self.draw_grid()
        self.draw_legend()

        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-2>", self._on_right_click)
        self.bind("<Button-3>", self._on_right_click)
        self.bind("<Shift-Button-1>", self._on_shift_click)
        self.bind("<Control-Button-1>", self._on_ctrl_click)

    def reset(self, grid: GridState) -> None:
        """Swap in a new grid and redraw from scratch."""
        self._grid = grid
        self.delete("all")
        self.draw_grid()
        self.draw_legend()

    def draw_grid(self) -> None:
        """Draw all grid cells using CELL_COLORS; keep overlays intact."""
        self.delete("cell")
        cs = self._cs
        for r in range(self._grid.rows):
            for c in range(self._grid.cols):
                cell = self._grid.get_cell_type(r, c)
                color = CELL_COLORS.get(cell, "white")
                x0, y0 = c * cs, r * cs
                self.create_rectangle(
                    x0, y0, x0 + cs, y0 + cs, fill=color, outline="lightgray", tags="cell"
                )
        sp = self._grid.start_pos
        gp = self._grid.goal_pos
        self._label_cell(sp.row, sp.col, "S", "black")
        self._label_cell(gp.row, gp.col, "G", "black")

    def draw_agent(self, row: int, col: int, color: str = "blue") -> None:
        """Draw a filled circle for the drone at (row, col)."""
        self.delete(self._AGENT_TAG)
        cs = self._cs
        pad = cs // 5
        x0, y0 = col * cs + pad, row * cs + pad
        self.create_oval(
            x0, y0, x0 + cs - 2 * pad, y0 + cs - 2 * pad, fill=color, outline="navy", tags=self._AGENT_TAG
        )

    def update_agent_position(self, row: int, col: int) -> None:
        """Erase old agent circle and redraw at new position."""
        self.draw_agent(row, col)

    def _label_cell(self, row: int, col: int, text: str, fg: str) -> None:
        """Draw a text label (e.g. S/G) in a cell."""
        cs = self._cs
        self.create_text(
            col * cs + cs // 2, row * cs + cs // 2, text=text, fill=fg, font=("Arial", 10, "bold"), tags="cell"
        )

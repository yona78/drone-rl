"""
EnvironmentEditor — mouse-driven grid cell editor (Phase 5).

Left-click cycles cell type; right-click opens a context menu.
Shift+click sets start; Ctrl+click sets goal.
Never imports from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §3.2.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import Menu

from ..constants import CELL_COLORS
from ..types.grid import CellType, Coordinate, GridState

_CYCLE_ORDER = [
    CellType.EMPTY, CellType.BUILDING, CellType.TRAP, CellType.CROSSWIND,
]


class EnvironmentEditor(tk.Canvas):
    """
    Interactive grid canvas that lets users paint cell types.

    **Input Data:** GridState, cell_size, optional on_change callback.
    **Output Data:** Modified GridState (in-place); redraws canvas.
    **Setup Data:** Mouse bindings registered in __init__.
    """

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
        w = grid.cols * cell_size + 2
        h = grid.rows * cell_size + 2
        super().__init__(parent, width=w, height=h, bg="white",
                         cursor="crosshair")
        self._draw_all()
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<Shift-Button-1>", self._on_shift_click)
        self.bind("<Control-Button-1>", self._on_ctrl_click)

    def _draw_all(self) -> None:
        self.delete("all")
        for r in range(self._grid.rows):
            for c in range(self._grid.cols):
                self._draw_cell(r, c)
        sp = self._grid.start_pos
        gp = self._grid.goal_pos
        self._label(sp.row, sp.col, "S", "white")
        self._label(gp.row, gp.col, "G", "black")

    def _draw_cell(self, row: int, col: int) -> None:
        cs = self._cs
        cell = self._grid.get_cell_type(row, col)
        color = CELL_COLORS.get(cell, "white")
        x0, y0 = col * cs, row * cs
        self.create_rectangle(x0, y0, x0 + cs, y0 + cs,
                               fill=color, outline="lightgray")

    def _label(self, row: int, col: int, text: str, fg: str) -> None:
        cs = self._cs
        self.create_text(col * cs + cs // 2, row * cs + cs // 2,
                          text=text, fill=fg, font=("Arial", 10, "bold"))

    def _cell_at(self, event: tk.Event) -> tuple[int, int]:
        return event.y // self._cs, event.x // self._cs

    def _on_left_click(self, event: tk.Event) -> None:
        r, c = self._cell_at(event)
        if not self._in_bounds(r, c):
            return
        current = self._grid.get_cell_type(r, c)
        idx = (_CYCLE_ORDER.index(current)
               if current in _CYCLE_ORDER else 0)
        next_type = _CYCLE_ORDER[(idx + 1) % len(_CYCLE_ORDER)]
        self.set_cell_type(r, c, next_type)

    def on_right_click(self, event: tk.Event) -> None:
        """Open a context menu for explicit cell type selection."""
        r, c = self._cell_at(event)
        if not self._in_bounds(r, c):
            return
        menu = Menu(self, tearoff=0)
        for ct in _CYCLE_ORDER:
            menu.add_command(
                label=ct.value.capitalize(),
                command=lambda t=ct, row=r, col=c: self.set_cell_type(row, col, t),
            )
        menu.add_separator()
        menu.add_command(label="Set Start",
                         command=lambda: self.set_start_position(r, c))
        menu.add_command(label="Set Goal",
                         command=lambda: self.set_goal_position(r, c))
        menu.tk_popup(event.x_root, event.y_root)

    def _on_shift_click(self, event: tk.Event) -> None:
        r, c = self._cell_at(event)
        if self._in_bounds(r, c):
            self.set_start_position(r, c)

    def _on_ctrl_click(self, event: tk.Event) -> None:
        r, c = self._cell_at(event)
        if self._in_bounds(r, c):
            self.set_goal_position(r, c)

    def set_cell_type(self, row: int, col: int, cell_type: CellType) -> None:
        """Update grid_state and redraw the affected cell."""
        self._grid.cells[(row, col)] = cell_type
        self._draw_all()
        if self._on_change:
            self._on_change()

    def set_start_position(self, row: int, col: int) -> None:
        """Relocate the start marker."""
        self._grid.start_pos = Coordinate(row, col)
        self._draw_all()
        if self._on_change:
            self._on_change()

    def set_goal_position(self, row: int, col: int) -> None:
        """Relocate the goal marker."""
        self._grid.goal_pos = Coordinate(row, col)
        self._draw_all()
        if self._on_change:
            self._on_change()

    def clear_grid(self) -> None:
        """Reset every cell to EMPTY."""
        self._grid.cells.clear()
        self._draw_all()
        if self._on_change:
            self._on_change()

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self._grid.rows and 0 <= col < self._grid.cols

"""CanvasEditingMixin — Interactive grid editing logic for GridCanvas."""

from __future__ import annotations

import tkinter as tk
from tkinter import Menu

from ..types.grid import CellType, Coordinate

_CYCLE_ORDER = [
    CellType.EMPTY,
    CellType.BUILDING,
    CellType.TRAP,
    CellType.CROSSWIND,
]


class CanvasEditingMixin:
    """Provides mouse-driven editing for a GridCanvas.

    Input Data: tk.Event coordinates; GridState reference.
    Output Data: Modified GridState; calls draw_grid() on the host.
    """

    def _cell_at(self, event: tk.Event) -> tuple[int, int]:
        """Convert pixel (x, y) to (row, col)."""
        return event.y // self._cs, event.x // self._cs

    def _on_left_click(self, event: tk.Event) -> None:
        """Cycle the cell type at the clicked position."""
        r, c = self._cell_at(event)
        if not self._in_bounds(r, c):
            return
        current = self._grid.get_cell_type(r, c)
        idx = _CYCLE_ORDER.index(current) if current in _CYCLE_ORDER else 0
        next_type = _CYCLE_ORDER[(idx + 1) % len(_CYCLE_ORDER)]
        self._set_cell_type(r, c, next_type)

    def _on_right_click(self, event: tk.Event) -> None:
        """Open context menu to pick cell type or set Start/Goal."""
        r, c = self._cell_at(event)
        if not self._in_bounds(r, c):
            return
        menu = Menu(self, tearoff=0)
        for ct in _CYCLE_ORDER:
            # Capture ct, r, c in lambda
            menu.add_command(
                label=ct.value.capitalize(),
                command=lambda t=ct, row=r, col=c: self._set_cell_type(row, col, t),
            )
        menu.add_separator()
        menu.add_command(
            label="Set Start", command=lambda row=r, col=c: self._set_start_position(row, col)
        )
        menu.add_command(
            label="Set Goal", command=lambda row=r, col=c: self._set_goal_position(row, col)
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _on_shift_click(self, event: tk.Event) -> None:
        """Relocate 'Start' (S) marker."""
        r, c = self._cell_at(event)
        if self._in_bounds(r, c):
            self._set_start_position(r, c)

    def _on_ctrl_click(self, event: tk.Event) -> None:
        """Relocate 'Goal' (G) marker."""
        r, c = self._cell_at(event)
        if self._in_bounds(r, c):
            self._set_goal_position(r, c)

    def set_cell_type(self, row: int, col: int, cell_type: CellType) -> None:
        """Exposed setter for programmatic use."""
        self._set_cell_type(row, col, cell_type)

    def set_start_position(self, row: int, col: int) -> None:
        """Exposed setter for programmatic use."""
        self._set_start_position(row, col)

    def set_goal_position(self, row: int, col: int) -> None:
        """Exposed setter for programmatic use."""
        self._set_goal_position(row, col)

    def _set_cell_type(self, row: int, col: int, cell_type: CellType) -> None:
        """Update grid cells (ignoring S/G protected cells)."""
        if (row, col) in (
            (self._grid.start_pos.row, self._grid.start_pos.col),
            (self._grid.goal_pos.row, self._grid.goal_pos.col),
        ):
            return
        self._grid.cells[(row, col)] = cell_type
        self.draw_grid()
        if self._on_change:
            self._on_change()

    def _set_start_position(self, row: int, col: int) -> None:
        """Relocate start pos and redraw."""
        # Clear any obstacle at new start position
        self._grid.cells.pop((row, col), None)
        self._grid.start_pos = Coordinate(row, col)
        self.draw_grid()
        self.draw_agent(row, col)  # Move drone to new start
        if self._on_change:
            self._on_change()

    def _set_goal_position(self, row: int, col: int) -> None:
        """Relocate goal pos and redraw."""
        # Clear any obstacle at new goal position
        self._grid.cells.pop((row, col), None)
        self._grid.goal_pos = Coordinate(row, col)
        self.draw_grid()
        if self._on_change:
            self._on_change()

    def _in_bounds(self, row: int, col: int) -> bool:
        """Check if grid coordinates are valid."""
        return 0 <= row < self._grid.rows and 0 <= col < self._grid.cols

    def clear_grid(self) -> None:
        """Reset every cell to EMPTY and redraw."""
        self._grid.cells.clear()
        self.draw_grid()
        if self._on_change:
            self._on_change()

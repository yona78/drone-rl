"""
GridCanvas — tkinter canvas renderer for the RL grid (Phase 5).

Draws cells, agent, path, directional policy arrows, and a persistent
color legend. Never imports from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §3.2.
"""

from __future__ import annotations

import tkinter as tk

from ..constants import CELL_COLORS
from ..types.grid import GridState

# Arrow direction deltas for policy overlay (row_delta, col_delta)
_ARROW_DELTAS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

LEGEND_ITEMS = [
    ("White", "Empty"),
    ("green", "Start"),
    ("gold", "Goal"),
    ("gray", "Building"),
    ("red", "Trap"),
    ("dodger blue", "Crosswind"),
    ("blue", "Drone"),
]


class GridCanvas(tk.Canvas):
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
    ) -> None:
        self._grid = grid
        self._cs = cell_size
        w = grid.cols * cell_size + 120  # +120 for legend
        h = grid.rows * cell_size + 2
        super().__init__(parent, width=w, height=h, bg="white")
        self.draw_grid()
        self.draw_legend()

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
                    x0,
                    y0,
                    x0 + cs,
                    y0 + cs,
                    fill=color,
                    outline="lightgray",
                    tags="cell",
                )
        sp = self._grid.start_pos
        gp = self._grid.goal_pos
        self._label_cell(sp.row, sp.col, "S", "white")
        self._label_cell(gp.row, gp.col, "G", "black")

    def draw_agent(self, row: int, col: int, color: str = "blue") -> None:
        """Draw a filled circle for the drone at (row, col)."""
        self.delete(self._AGENT_TAG)
        cs = self._cs
        pad = cs // 5
        x0, y0 = col * cs + pad, row * cs + pad
        self.create_oval(
            x0,
            y0,
            x0 + cs - 2 * pad,
            y0 + cs - 2 * pad,
            fill=color,
            outline="navy",
            tags=self._AGENT_TAG,
        )

    def update_agent_position(self, row: int, col: int) -> None:
        """Erase old agent circle and redraw at new position."""
        self.draw_agent(row, col)

    def draw_path(self, path: list[tuple[int, int]]) -> None:
        """Draw a polyline tracing the agent's trajectory."""
        self.delete(self._PATH_TAG)
        if len(path) < 2:
            return
        cs = self._cs
        half = cs // 2
        pts = [c * cs + half for rc in path for c in (rc[1], rc[0])]
        self.create_line(*pts, fill="navy", width=2, arrow=tk.LAST, tags=self._PATH_TAG)

    def clear(self) -> None:
        """Remove agent, path, and arrow overlays; keep cell background."""
        for tag in (self._AGENT_TAG, self._PATH_TAG, self._ARROW_TAG):
            self.delete(tag)

    def draw_policy_arrows(self, qtable: dict) -> None:
        """Draw argmax-Q directional arrows for each cell in the Q-table."""
        self.delete(self._ARROW_TAG)
        cs = self._cs
        half = cs // 2
        for state_key, actions in qtable.items():
            if not actions:
                continue
            best = max(actions, key=actions.get)
            dr, dc = _ARROW_DELTAS.get(best, (0, 0))
            if dr == 0 and dc == 0:
                continue
            parts = state_key.split(",")
            if len(parts) != 2:
                continue
            r, c = int(parts[0]), int(parts[1])
            cx, cy = c * cs + half, r * cs + half
            ex, ey = cx + dc * (half - 4), cy + dr * (half - 4)
            self.create_line(
                cx, cy, ex, ey, arrow=tk.LAST, fill="black", width=1, tags=self._ARROW_TAG
            )

    def draw_legend(self) -> None:
        """Draw a persistent color legend to the right of the grid."""
        x_off = self._grid.cols * self._cs + 10
        for i, (color, label) in enumerate(LEGEND_ITEMS):
            y = 20 + i * 22
            self.create_rectangle(x_off, y, x_off + 16, y + 16, fill=color, outline="black")
            self.create_text(x_off + 22, y + 8, text=label, anchor=tk.W, font=("Arial", 9))

    def _label_cell(self, row: int, col: int, text: str, fg: str) -> None:
        cs = self._cs
        self.create_text(
            col * cs + cs // 2,
            row * cs + cs // 2,
            text=text,
            fill=fg,
            font=("Arial", 10, "bold"),
            tags="cell",
        )

"""CanvasOverlayMixin for drawing paths, policies, and legends."""

from __future__ import annotations

import tkinter as tk

_ARROW_DELTAS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

LEGEND_ITEMS = [
    ("white", "Empty"),
    ("green", "Start"),
    ("gold", "Goal"),
    ("gray", "Building"),
    ("red", "Trap"),
    ("dodger blue", "Crosswind"),
    ("blue", "Drone"),
]


class CanvasOverlayMixin:
    """Provides methods for drawing paths, policies, and overlays on a Canvas.

    Input Data: path lists, Q-table dicts, grid dimensions from host canvas.
    Output Data: drawn tk.Canvas items (lines, polygons, text).
    Setup Data: _cs (cell size), _PATH_TAG, _POLICY_TAG from host GridCanvas.
    """

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
            self.create_text(
                x_off + 22, y + 8, text=label, anchor=tk.W, font=("Arial", 9), fill="black"
            )

"""DroneRLApp — Main tkinter application window (Phase 5, §4 SDK boundary)."""

from __future__ import annotations

import tkinter as tk

from ..sdk import DroneRLSDK
from ..shared.version import __version__
from ..types.grid import Coordinate, GridState
from .app_ui_mixin import AppUIMixin


class DroneRLApp(tk.Tk, AppUIMixin):
    """
    Main application window for 2D Drone Pathfinding RL Simulation.

    **Input Data:** DroneRLSDK instance (injected).
    **Output Data:** tkinter window with live grid, charts, and controls.
    **Setup Data:** All sub-frames wired in create_ui(); SDK stored as ref.
    """

    def __init__(self, sdk: DroneRLSDK | None = None) -> None:
        super().__init__()
        self.sdk = sdk or DroneRLSDK()
        self.title(f"2D Drone Pathfinding RL Simulation v{__version__}")
        self.geometry("1400x900")
        self.resizable(True, True)
        self._build_default_grid()
        self.create_ui()

    def _build_default_grid(self) -> None:
        """Initialise SDK with a default 10×10 empty grid."""
        grid = GridState(
            rows=10,
            cols=10,
            cells={},
            start_pos=Coordinate(0, 0),
            goal_pos=Coordinate(9, 9),
        )
        self.sdk.create_environment(grid)
        self._grid = grid

    def _refresh_all(self) -> None:
        """Redraw canvas + charts after a training update."""
        self._grid_canvas.draw_grid()
        stats = self.sdk.get_episode_stats()
        if not stats:
            return
        last = stats[-1]
        self._conv_chart.update(stats)
        self._heatmap.update(self.sdk.get_qtable())
        self._stats_panel.update(
            last["episode"],
            last["total_reward"],
            last["steps"],
            last["terminal_reason"],
            last["epsilon"],
        )

    def _set_status(self, msg: str) -> None:
        self._status_var.set(msg)

    def _save_policy(self) -> None:
        from tkinter.filedialog import asksaveasfilename

        p = asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if p:
            self.sdk.save_policy(p)
            self._set_status(f"Policy saved → {p}")

    def _load_policy(self) -> None:
        from tkinter.filedialog import askopenfilename

        p = askopenfilename(filetypes=[("JSON", "*.json")])
        if p:
            self.sdk.load_policy(p)
            self._set_status(f"Policy loaded ← {p}")

    def _reset_grid(self) -> None:
        self._build_default_grid()
        self._grid_canvas.reset(self._grid)
        self._set_status("Grid reset.")

    def _show_about(self) -> None:
        from tkinter.messagebox import showinfo

        showinfo("About", f"2D Drone Pathfinding RL Simulation\nv{__version__}")

    def run(self) -> None:
        """Start the tkinter event loop."""
        self.mainloop()

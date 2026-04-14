"""DroneRLApp — Main tkinter application window (Phase 5, §4 SDK boundary)."""

from __future__ import annotations

import tkinter as tk

from ..sdk import DroneRLSDK
from ..shared.version import __version__
from ..types.grid import Coordinate, GridState
from .app_menu import AppMenuMixin
from .app_ui_mixin import AppUIMixin


class DroneRLApp(tk.Tk, AppUIMixin, AppMenuMixin):
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
        self._refresh_all()

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

    def _refresh_all(self, msg: dict | None = None) -> None:
        """Redraw canvas + charts. Handle both single episode and step updates."""
        # Sync grid from SDK if it changed (e.g. after load_layout)
        new_grid = self.sdk.get_grid()
        if new_grid is not None and new_grid is not self._grid:
            self._grid = new_grid
            self._grid_canvas.reset(new_grid)

        # Update drone if a step message was received
        if msg and msg.get("type") == "step":
            self._grid_canvas.draw_agent(msg["row"], msg["col"])
            return

        # Default: Full redraw
        self._grid_canvas.draw_grid()
        agent_pos = self.sdk.get_agent_state()
        self._grid_canvas.draw_agent(agent_pos["row"], agent_pos["col"])

        qtable = self.sdk.get_qtable()
        self._heatmap.update(qtable)
        self._inspector.update(qtable)

        stats = self.sdk.get_episode_stats()
        if not stats:
            return
        last = stats[-1]
        self._conv_chart.update(stats)
        self._stats_panel.update(
            last["episode"],
            last["total_reward"],
            last["steps"],
            last["terminal_reason"],
            last["epsilon"],
        )

    def _set_status(self, msg: str) -> None:
        self._status_var.set(msg)

    def run(self) -> None:
        """Start the tkinter event loop."""
        self.mainloop()

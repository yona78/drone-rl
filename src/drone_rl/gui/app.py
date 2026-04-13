"""DroneRLApp — Main tkinter application window (Phase 5, §4 SDK boundary)."""

from __future__ import annotations

import tkinter as tk

from ..sdk import DroneRLSDK
from ..shared.version import __version__
from ..types.grid import Coordinate, GridState


class DroneRLApp(tk.Tk):
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

    def create_ui(self) -> None:
        """Build and layout all sub-frames."""
        self._build_menu()
        # Top: hyperparameter + playback + IO controls
        self._ctrl_frame = tk.Frame(self, bd=1, relief=tk.RIDGE)
        self._ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)
        self._build_controls(self._ctrl_frame)
        # Main body: canvas (left) + charts (right)
        body = tk.Frame(self)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=2)
        self._canvas_frame = tk.LabelFrame(body, text="Grid", padx=2, pady=2)
        self._canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._chart_frame = tk.LabelFrame(body, text="Analytics", padx=2, pady=2)
        self._chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_canvas(self._canvas_frame)
        self._build_charts(self._chart_frame)
        # Bottom: status bar
        self._status_var = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self._status_var, anchor=tk.W, relief=tk.SUNKEN).pack(
            side=tk.BOTTOM, fill=tk.X
        )

    def _build_menu(self) -> None:
        """Create File / Edit / Help menu bar."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Policy", command=self._save_policy)
        file_menu.add_command(label="Load Policy", command=self._load_policy)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Reset Grid", command=self._reset_grid)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _build_controls(self, parent: tk.Frame) -> None:
        from .hyperparameter_panel import HyperparameterPanel
        from .io_panel import IOPanel
        from .playback_controls import PlaybackControls

        self._hp_panel = HyperparameterPanel(parent, self.sdk, self._set_status)
        self._hp_panel.pack(side=tk.LEFT, padx=4)
        self._pb_controls = PlaybackControls(
            parent,
            self.sdk,
            self._set_status,
            self._refresh_all,
            self._hp_panel.get_hyperparameters,
        )
        self._pb_controls.pack(side=tk.LEFT, padx=4)
        self._io_panel = IOPanel(parent, self.sdk, self._set_status)
        self._io_panel.pack(side=tk.LEFT, padx=4)

    def _build_canvas(self, parent: tk.Frame) -> None:
        from .canvas import GridCanvas

        self._grid_canvas = GridCanvas(parent, self._grid, cell_size=50)
        self._grid_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_charts(self, parent: tk.Frame) -> None:
        from .charts import ConvergenceChart, QValueHeatmap
        from .panels import EpisodeStatsPanel, QTableInspectorPanel

        self._conv_chart = ConvergenceChart(parent)
        self._conv_chart.get_widget().pack(fill=tk.BOTH, expand=True)
        self._heatmap = QValueHeatmap(parent, self._grid.rows, self._grid.cols)
        self._heatmap.get_widget().pack(fill=tk.BOTH, expand=True)
        self._stats_panel = EpisodeStatsPanel(parent)
        self._stats_panel.pack(fill=tk.X)
        self._inspector = QTableInspectorPanel(parent)
        self._inspector.pack(fill=tk.X)

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

        from ..shared.version import __version__

        showinfo("About", f"2D Drone Pathfinding RL Simulation\nv{__version__}")

    def run(self) -> None:
        """Start the tkinter event loop."""
        self.mainloop()

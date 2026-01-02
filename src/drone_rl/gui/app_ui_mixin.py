"""AppUIMixin — UI builder methods for the main application window."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import DroneRLApp


class AppUIMixin:
    """Mixin for building the tkinter UI layout.

    Input Data: DroneRLApp host (self) providing sdk, _grid references.
    Output Data: populated tk.Frame hierarchy, widget references on host.
    Setup Data: none — layout is built once during create_ui().
    """

    def create_ui(self: DroneRLApp) -> None:
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

    def _build_menu(self: DroneRLApp) -> None:
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

    def _build_controls(self: DroneRLApp, parent: tk.Frame) -> None:
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

    def _build_canvas(self: DroneRLApp, parent: tk.Frame) -> None:
        from .canvas import GridCanvas

        self._grid_canvas = GridCanvas(parent, self._grid, cell_size=50)
        self._grid_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_charts(self: DroneRLApp, parent: tk.Frame) -> None:
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

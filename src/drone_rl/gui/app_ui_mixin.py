"""AppUIMixin — UI builder methods for the main application window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
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
        self._io_panel = IOPanel(
            parent,
            self.sdk,
            self._set_status,
            self._open_editor,
            self._refresh_all,
            self._clear_grid,
        )
        self._io_panel.pack(side=tk.LEFT, padx=4)

    def _build_canvas(self: DroneRLApp, parent: tk.Frame) -> None:
        from .canvas import GridCanvas

        # Make grid scrollable
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        canvas_scroll = tk.Canvas(container, highlightthickness=0)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas_scroll.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=canvas_scroll.xview)
        
        self._grid_canvas = GridCanvas(canvas_scroll, self._grid, cell_size=50, on_change=self._refresh_all)
        
        # Update scrollregion
        def _on_grid_resize(e: tk.Event) -> None:
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))

        self._grid_canvas.bind("<Configure>", _on_grid_resize)

        canvas_scroll.create_window((0, 0), window=self._grid_canvas, anchor="nw")
        canvas_scroll.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        # Mouse wheel support for grid
        def _on_grid_wheel(event: tk.Event) -> None:
            canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas_scroll.bind_all("<MouseWheel>", _on_grid_wheel)

    def _build_charts(self: DroneRLApp, parent: tk.Frame) -> None:
        from .charts import ConvergenceChart, QValueHeatmap
        from .panels import EpisodeStatsPanel, QTableInspectorPanel

        # Make analytics scrollable
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Update scrollregion on resize
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create window inside canvas
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Fix frame width to match canvas width
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel support
        def _on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._conv_chart = ConvergenceChart(scrollable_frame)
        self._conv_chart.get_widget().pack(fill=tk.X)
        self._heatmap = QValueHeatmap(scrollable_frame, self._grid.rows, self._grid.cols)
        self._heatmap.get_widget().pack(fill=tk.X)
        self._stats_panel = EpisodeStatsPanel(scrollable_frame)
        self._stats_panel.pack(fill=tk.X, pady=5)
        self._inspector = QTableInspectorPanel(scrollable_frame)
        self._inspector.pack(fill=tk.X, pady=5)

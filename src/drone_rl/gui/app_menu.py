"""AppMenuMixin for Drone RL GUI application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import DroneRLApp


class AppMenuMixin:
    """Provides menu bar building functionality for DroneRLApp.

    Input Data: host DroneRLApp (self) providing sdk, _grid, _set_status.
    Output Data: tkinter Menu bar with File/Edit/Help cascades.
    Setup Data: none — menu is built once during _build_menu().
    """

    def _build_menu(self: DroneRLApp) -> None:
        """Create File / Edit / Help menu bar."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Policy", command=self._save_policy)
        file_menu.add_command(label="Load Policy", command=self._load_policy)
        file_menu.add_separator()
        file_menu.add_command(label="Save Layout", command=self._save_layout)
        file_menu.add_command(label="Load Layout", command=self._load_layout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Edit Grid...", command=self._open_editor)
        edit_menu.add_command(label="Clear Grid", command=self._clear_grid)
        edit_menu.add_command(label="Reset Grid", command=self._reset_grid)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _save_policy(self: DroneRLApp) -> None:
        from tkinter.filedialog import asksaveasfilename

        p = asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if p:
            try:
                self.sdk.save_policy(p)
                self._set_status(f"Policy saved → {p}")
            except Exception as exc:
                self._set_status(f"Error saving policy: {exc}")

    def _load_policy(self: DroneRLApp) -> None:
        from tkinter.filedialog import askopenfilename

        p = askopenfilename(filetypes=[("JSON", "*.json")])
        if p:
            try:
                self.sdk.load_policy(p)
                self._set_status(f"Policy loaded ← {p}")
                self._refresh_all()
            except Exception as exc:
                self._set_status(f"Error loading policy: {exc}")

    def _save_layout(self: DroneRLApp) -> None:
        from tkinter.filedialog import asksaveasfilename

        p = asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if p:
            try:
                self.sdk.save_layout(p)
                self._set_status(f"Layout saved → {p}")
            except Exception as exc:
                self._set_status(f"Error saving layout: {exc}")

    def _load_layout(self: DroneRLApp) -> None:
        from tkinter.filedialog import askopenfilename

        p = askopenfilename(filetypes=[("JSON", "*.json")])
        if p:
            try:
                self.sdk.load_layout(p)
                self._set_status(f"Layout loaded ← {p}")
                self._refresh_all()
            except Exception as exc:
                self._set_status(f"Error loading layout: {exc}")

    def _open_editor(self: DroneRLApp) -> None:
        from .editor import EnvironmentEditor

        top = tk.Toplevel(self)
        top.title("Grid Editor")
        top.transient(self)
        top.grab_set()

        editor = EnvironmentEditor(top, self._grid, cell_size=50, on_change=self._refresh_all)
        editor.pack(padx=10, pady=10)

        instr = tk.Label(
            top,
            text="L-Click: Cycle Type | R-Click: Menu | Shift+Click: Start | Ctrl+Click: Goal",
            font=("Arial", 9, "italic"),
        )
        instr.pack(pady=5)
        ttk.Button(top, text="Done", command=top.destroy).pack(pady=5)

    def _clear_grid(self: DroneRLApp) -> None:
        self._grid_canvas.clear_grid()
        self._set_status("Grid cleared.")

    def _reset_grid(self: DroneRLApp) -> None:
        self._build_default_grid()
        self._grid_canvas.reset(self._grid)
        self._set_status("Grid reset.")

    def _show_about(self: DroneRLApp) -> None:
        from tkinter.messagebox import showinfo

        from ..shared.version import __version__

        showinfo("About", f"2D Drone Pathfinding RL Simulation\nv{__version__}")

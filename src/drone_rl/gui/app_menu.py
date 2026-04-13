"""AppMenuMixin for Drone RL GUI application."""

from __future__ import annotations

import tkinter as tk


class AppMenuMixin:
    """Provides menu bar building functionality for DroneRLApp."""

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

"""
IOPanel — Save / Load / Export file-dialog buttons (Phase 5).

All file I/O operations delegate to DroneRLSDK. No direct RL imports (§4).

Reference: CODE_PLAN Phase 5, Dr. Segal §4.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import filedialog

from ..sdk import DroneRLSDK

_JSON_TYPE = [("JSON file", "*.json")]
_CSV_TYPE = [("CSV file", "*.csv")]


class IOPanel(tk.LabelFrame):
    """
    Panel with Save/Load policy, Save/Load layout, and Export log buttons.

    **Input Data:** SDK reference; optional status callback.
    **Output Data:** Triggers SDK I/O methods with user-chosen file paths.
    **Setup Data:** File dialog filters defined as module-level constants.
    """

    def __init__(
        self,
        parent: tk.Widget,
        sdk: DroneRLSDK,
        status_cb: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent, text="File I/O", padx=4, pady=2)
        self._sdk = sdk
        self._status_cb = status_cb
        self._build()

    def _build(self) -> None:
        btn_cfg = {"width": 14, "pady": 2}
        row = 0
        tk.Button(self, text="Save Policy", command=self._save_policy, **btn_cfg).grid(
            row=row, column=0, padx=2
        )
        tk.Button(self, text="Load Policy", command=self._load_policy, **btn_cfg).grid(
            row=row, column=1, padx=2
        )
        row += 1
        tk.Button(self, text="Save Layout", command=self._save_layout, **btn_cfg).grid(
            row=row, column=0, padx=2
        )
        tk.Button(self, text="Load Layout", command=self._load_layout, **btn_cfg).grid(
            row=row, column=1, padx=2
        )
        row += 1
        tk.Button(self, text="Export Episode Log", command=self._export_logs, **btn_cfg).grid(
            row=row, column=0, columnspan=2, padx=2
        )

    def _save_policy(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=_JSON_TYPE, title="Save Policy"
        )
        if path:
            self._sdk.save_policy(path)
            self._set_status(f"Policy saved → {path}")

    def _load_policy(self) -> None:
        path = filedialog.askopenfilename(filetypes=_JSON_TYPE, title="Load Policy")
        if path:
            self._sdk.load_policy(path)
            self._set_status(f"Policy loaded ← {path}")

    def _save_layout(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=_JSON_TYPE, title="Save Layout"
        )
        if path:
            self._sdk.save_layout(path)
            self._set_status(f"Layout saved → {path}")

    def _load_layout(self) -> None:
        path = filedialog.askopenfilename(filetypes=_JSON_TYPE, title="Load Layout")
        if path:
            self._sdk.load_layout(path)
            self._set_status(f"Layout loaded ← {path}")

    def _export_logs(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=_CSV_TYPE, title="Export Episode Log"
        )
        if path:
            self._sdk.export_logs(path)
            self._set_status(f"Logs exported → {path}")

    def _set_status(self, msg: str) -> None:
        if self._status_cb:
            self._status_cb(msg)

"""
PlaybackControls — Train / Pause / Reset / Step buttons (Phase 5).

All button callbacks delegate to the DroneRLSDK. The panel never calls
into drone_rl.rl directly (§4 boundary).

Reference: CODE_PLAN Phase 5, Dr. Segal §4.
"""

from __future__ import annotations

import threading
import tkinter as tk
from collections.abc import Callable

from ..sdk import DroneRLSDK
from ..types.agent import Action


class PlaybackControls(tk.LabelFrame):
    """
    Control panel with Train, Pause, Reset, Step buttons and speed slider.

    **Input Data:** SDK reference; status and refresh callbacks.
    **Output Data:** Triggers SDK methods; calls refresh_cb after training.
    **Setup Data:** Training thread managed internally to keep UI responsive.
    """

    def __init__(
        self,
        parent: tk.Widget,
        sdk: DroneRLSDK,
        status_cb: Callable[[str], None] | None = None,
        refresh_cb: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent, text="Controls", padx=4, pady=2)
        self._sdk = sdk
        self._status_cb = status_cb
        self._refresh_cb = refresh_cb
        self._training_thread: threading.Thread | None = None
        self._speed_var = tk.IntVar(value=30)
        self._build()

    def _build(self) -> None:
        btn_cfg = {"width": 8, "padx": 2}
        tk.Button(self, text="Train", command=self._on_train,
                  bg="#4caf50", fg="white", **btn_cfg).grid(
            row=0, column=0, padx=2, pady=2)
        tk.Button(self, text="Pause", command=self._on_pause,
                  bg="#ff9800", fg="white", **btn_cfg).grid(
            row=0, column=1, padx=2, pady=2)
        tk.Button(self, text="Reset", command=self._on_reset,
                  bg="#f44336", fg="white", **btn_cfg).grid(
            row=0, column=2, padx=2, pady=2)
        tk.Button(self, text="Step", command=self._on_step,
                  bg="#2196f3", fg="white", **btn_cfg).grid(
            row=0, column=3, padx=2, pady=2)
        tk.Label(self, text="Speed (fps):").grid(row=1, column=0,
                                                  columnspan=2, sticky=tk.E)
        tk.Scale(self, variable=self._speed_var, from_=1, to=120,
                 orient=tk.HORIZONTAL, length=120).grid(
            row=1, column=2, columnspan=2, sticky=tk.W)

    def _on_train(self) -> None:
        """Launch training in a background thread."""
        if self._training_thread and self._training_thread.is_alive():
            self._set_status("Already training.")
            return
        self._sdk.resume()
        self._set_status("Training…")
        self._training_thread = threading.Thread(
            target=self._train_worker, daemon=True)
        self._training_thread.start()

    def _train_worker(self) -> None:
        """Background thread: run training, then schedule a UI refresh."""
        try:
            self._sdk.train()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Training error: {exc}")
            return
        self.after(0, self._on_training_done)

    def _on_training_done(self) -> None:
        stats = self._sdk.get_episode_stats()
        n = len(stats)
        last_r = stats[-1]["total_reward"] if stats else 0.0
        self._set_status(f"Done — {n} episodes, last reward {last_r:.1f}")
        if self._refresh_cb:
            self._refresh_cb()

    def _on_pause(self) -> None:
        self._sdk.pause()
        self._set_status("Paused.")

    def _on_reset(self) -> None:
        self._sdk.reset()
        self._set_status("Reset.")
        if self._refresh_cb:
            self._refresh_cb()

    def _on_step(self) -> None:
        _, reward, done = self._sdk.step(Action.RIGHT)
        msg = f"Step — reward {reward:.1f}"
        if done:
            msg += " [done]"
        self._set_status(msg)
        if self._refresh_cb:
            self._refresh_cb()

    def _set_status(self, msg: str) -> None:
        if self._status_cb:
            self._status_cb(msg)

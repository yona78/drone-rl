"""
PlaybackControls — Train / Pause / Reset / Step buttons (Phase 6).

Training runs in a daemon thread. EpisodeRecords are passed to the main
thread via queue.Queue polled with root.after(100, ...) — §15 thread safety.
All button callbacks delegate to the DroneRLSDK (§4 boundary).
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from ..sdk import DroneRLSDK


class PlaybackControls(tk.LabelFrame):
    """
    Control panel with Train, Pause, Reset, Step buttons and speed slider.

    **Input Data:** SDK reference; status, refresh, and get-hp callbacks.
    **Output Data:** Triggers SDK methods; polls update_queue for live charts.
    **Setup Data:** Daemon training thread + queue.Queue for thread safety.
    """

    def __init__(
        self,
        parent: tk.Widget,
        sdk: DroneRLSDK,
        status_cb: Callable[[str], None] | None = None,
        refresh_cb: Callable[[dict | None], None] | None = None,
        get_hp_cb: Callable[[], object] | None = None,
    ) -> None:
        super().__init__(parent, text="Controls", padx=4, pady=2)
        self._sdk = sdk
        self._status_cb = status_cb
        self._refresh_cb = refresh_cb
        self._get_hp_cb = get_hp_cb
        self._training_thread: threading.Thread | None = None
        self._update_queue: queue.Queue = queue.Queue(maxsize=1000)
        self._speed_var = tk.IntVar(value=30)
        self._visualise_var = tk.BooleanVar(value=True)
        self._build()

    def _build(self) -> None:
        self._train_btn = ttk.Button(self, text="Start/Resume", command=self._on_train)
        self._train_btn.grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(self, text="Pause", command=self._on_pause).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(self, text="Reset", command=self._on_reset).grid(row=0, column=2, padx=2, pady=2)
        ttk.Button(self, text="Step", command=self._on_step).grid(row=0, column=3, padx=2, pady=2)

        tk.Checkbutton(self, text="Visualise Training", variable=self._visualise_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W
        )

        tk.Label(self, text="Speed (fps):").grid(row=1, column=1, sticky=tk.E)
        tk.Scale(
            self, variable=self._speed_var, from_=1, to=120, orient=tk.HORIZONTAL, length=100
        ).grid(row=1, column=2, columnspan=2, sticky=tk.W)

    def _on_train(self) -> None:
        """Apply hyperparameters, then launch training in a background thread."""
        if self._training_thread and self._training_thread.is_alive():
            self._set_status("Already training.")
            return
        if self._get_hp_cb:
            self._sdk.update_hyperparameters(self._get_hp_cb())  # type: ignore[arg-type]
        self._sdk.resume()
        # Drain any stale items from a previous run
        while not self._update_queue.empty():
            try:
                self._update_queue.get_nowait()
            except queue.Empty:
                break
        self._set_status("Training…")
        fps = self._speed_var.get() if self._visualise_var.get() else 0
        self._training_thread = threading.Thread(
            target=self._train_worker, args=(fps,), daemon=True
        )
        self._training_thread.start()
        self.after(10, self._poll_queue)

    def _train_worker(self, fps: int = 0) -> None:
        """Background thread: run training, enqueue each EpisodeRecord."""
        try:
            self._sdk.train(update_queue=self._update_queue, fps=fps)
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Training error: {exc}")
            return
        self.after(0, self._on_training_done)

    def _poll_queue(self) -> None:
        """Drain the update queue on the main thread; reschedule if needed."""
        msg = None
        while True:
            try:
                msg = self._update_queue.get_nowait()
                if self._refresh_cb:
                    self._refresh_cb(msg)
            except queue.Empty:
                break

        still_running = bool(self._training_thread and self._training_thread.is_alive())
        if still_running or not self._update_queue.empty():
            self.after(10, self._poll_queue)

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
        agent, reward, done = self._sdk.step()
        msg = f"Step — reward {reward:.1f}"
        if done:
            msg += " [done]"
        self._set_status(msg)
        if self._refresh_cb:
            self._refresh_cb({"type": "step", "row": agent.position.row, "col": agent.position.col})

    def _set_status(self, msg: str) -> None:
        if self._status_cb:
            self._status_cb(msg)

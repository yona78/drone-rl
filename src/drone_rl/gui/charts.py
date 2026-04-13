"""
charts.py — ConvergenceChart and QValueHeatmap (Phase 5).

Both classes embed matplotlib figures inside a tkinter frame.
Never imports from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §5.5.
"""

from __future__ import annotations

import tkinter as tk

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402


class ConvergenceChart:
    """
    Line chart: total reward and 50-episode moving average vs episode number.

    **Input Data:** list[dict] with 'episode' and 'total_reward' keys.
    **Output Data:** Embedded matplotlib canvas widget.
    **Setup Data:** Figure created in __init__, updated on each update() call.
    """

    def __init__(self, parent: tk.Widget) -> None:
        self._fig, self._ax = plt.subplots(figsize=(4, 2.5), dpi=80)
        self._fig.tight_layout(pad=1.5)
        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        self._ax.set_title("Reward per Episode", fontsize=9)
        self._ax.set_xlabel("Episode", fontsize=8)
        self._ax.set_ylabel("Total Reward", fontsize=8)
        self._ax.tick_params(labelsize=7)

    def get_widget(self) -> tk.Widget:
        """Return the tkinter widget to pack into the parent frame."""
        return self._canvas.get_tk_widget()

    def update(self, episode_stats: list[dict]) -> None:
        """Redraw with new episode stats; overlay 50-ep moving average."""
        if not episode_stats:
            return
        eps = [s["episode"] for s in episode_stats]
        rewards = [s["total_reward"] for s in episode_stats]
        self._ax.cla()
        self._ax.set_title("Reward per Episode", fontsize=9)
        self._ax.set_xlabel("Episode", fontsize=8)
        self._ax.set_ylabel("Total Reward", fontsize=8)
        self._ax.tick_params(labelsize=7)
        self._ax.plot(eps, rewards, color="#1976d2", alpha=0.5, linewidth=0.8, label="Raw")
        window = 50
        if len(rewards) >= window:
            ma = [
                sum(rewards[max(0, i - window) : i]) / min(window, i)
                for i in range(1, len(rewards) + 1)
            ]
            self._ax.plot(eps, ma, color="#e53935", linewidth=1.5, label=f"{window}-ep avg")
            self._ax.legend(fontsize=7)
        self._canvas.draw()


class QValueHeatmap:
    """
    Heatmap of max Q-value per grid cell (blue=low → red=high).

    **Input Data:** Serialised Q-table dict from SDK.get_qtable().
    **Output Data:** Embedded matplotlib canvas widget.
    **Setup Data:** Grid dimensions from __init__; figure updated each call.
    """

    def __init__(self, parent: tk.Widget, rows: int, cols: int) -> None:
        self._rows = rows
        self._cols = cols
        self._fig, self._ax = plt.subplots(figsize=(3, 3), dpi=80)
        self._fig.tight_layout(pad=1.0)
        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        self._ax.set_title("Max Q-Value Heatmap", fontsize=9)
        self._im = None

    def get_widget(self) -> tk.Widget:
        """Return the tkinter widget to pack into the parent frame."""
        return self._canvas.get_tk_widget()

    def update(self, qtable: dict) -> None:
        """Rebuild the heatmap from the latest Q-table snapshot."""
        import numpy as np

        grid = np.zeros((self._rows, self._cols))
        for key, actions in qtable.items():
            parts = key.split(",")
            if len(parts) != 2:
                continue
            r, c = int(parts[0]), int(parts[1])
            if 0 <= r < self._rows and 0 <= c < self._cols and actions:
                grid[r, c] = max(actions.values())
        self._ax.cla()
        self._ax.set_title("Max Q-Value Heatmap", fontsize=9)
        self._ax.tick_params(labelsize=7)
        self._im = self._ax.imshow(
            grid,
            cmap="coolwarm",
            aspect="auto",
            origin="upper",
        )
        self._canvas.draw()

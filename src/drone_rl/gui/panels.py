"""
panels.py — EpisodeStatsPanel and QTableInspectorPanel (Phase 5).

Read-only info panels; never import from drone_rl.rl (§4 boundary).

Reference: CODE_PLAN Phase 5, §5.6.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class EpisodeStatsPanel(tk.LabelFrame):
    """
    Displays live stats for the most-recently completed episode.

    **Input Data:** episode_num, reward, steps, terminal_reason, epsilon.
    **Output Data:** Updated tkinter Label widgets.
    **Setup Data:** Five StringVar labels built in __init__.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, text="Episode Stats", padx=4, pady=2)
        self._ep_var = tk.StringVar(value="—")
        self._rew_var = tk.StringVar(value="—")
        self._steps_var = tk.StringVar(value="—")
        self._reason_var = tk.StringVar(value="—")
        self._eps_var = tk.StringVar(value="—")
        self._build()

    def _build(self) -> None:
        labels = [
            ("Episode:", self._ep_var),
            ("Reward:", self._rew_var),
            ("Steps:", self._steps_var),
            ("Terminal:", self._reason_var),
            ("Epsilon:", self._eps_var),
        ]
        for row, (lbl, var) in enumerate(labels):
            tk.Label(self, text=lbl, width=10, anchor=tk.E).grid(
                row=row, column=0, sticky=tk.E)
            tk.Label(self, textvariable=var, width=14, anchor=tk.W).grid(
                row=row, column=1, sticky=tk.W)

    def update(
        self,
        episode_num: int,
        reward: float,
        steps: int,
        reason: str,
        epsilon: float,
    ) -> None:
        """Refresh all stat labels with values from the latest episode."""
        self._ep_var.set(str(episode_num))
        self._rew_var.set(f"{reward:.2f}")
        self._steps_var.set(str(steps))
        self._reason_var.set(reason)
        self._eps_var.set(f"{epsilon:.4f}")


class QTableInspectorPanel(tk.LabelFrame):
    """
    Shows Q(s, a) values for a selected grid cell.

    **Input Data:** Serialised Q-table dict; selected_state tuple (row, col).
    **Output Data:** Updated ttk.Treeview with action→Q-value rows.
    **Setup Data:** Treeview + cell selector dropdown built in __init__.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, text="Q-Table Inspector", padx=4, pady=2)
        self._state_var = tk.StringVar(value="0,0")
        self._qtable: dict = {}
        self._build()

    def _build(self) -> None:
        top = tk.Frame(self)
        top.pack(fill=tk.X)
        tk.Label(top, text="State:").pack(side=tk.LEFT)
        self._state_entry = ttk.Entry(top, textvariable=self._state_var, width=8)
        self._state_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Inspect",
                   command=self._refresh).pack(side=tk.LEFT, padx=2)
        cols = ("Action", "Q-Value")
        self._tree = ttk.Treeview(self, columns=cols,
                                   show="headings", height=4)
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=90)
        self._tree.pack(fill=tk.X, pady=2)

    def update(self, qtable: dict, selected_state: tuple | None = None) -> None:
        """Store latest Q-table and optionally jump to selected_state."""
        self._qtable = qtable
        if selected_state is not None:
            self._state_var.set(f"{selected_state[0]},{selected_state[1]}")
        self._refresh()

    def _refresh(self) -> None:
        """Repopulate treeview for the current state key."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        key = self._state_var.get().strip()
        actions = self._qtable.get(key, {})
        for action, q_val in sorted(actions.items()):
            self._tree.insert("", tk.END, values=(action, f"{q_val:.4f}"))

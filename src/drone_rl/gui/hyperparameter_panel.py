"""
HyperparameterPanel — sliders and inputs for RL hyperparameters (Phase 5).

All values default from constants.py; get_hyperparameters() returns a
Hyperparameters dataclass for the SDK. Never imports from drone_rl.rl (§4).

Reference: CODE_PLAN Phase 5, Dr. Segal §4.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from ..constants import (
    ALPHA_DEFAULT,
    EPSILON_DECAY_DEFAULT,
    EPSILON_DEFAULT,
    EPSILON_MIN_DEFAULT,
    GAMMA_DEFAULT,
    MAX_STEPS_DEFAULT,
    RANDOM_SEED_DEFAULT,
    TOTAL_EPISODES_DEFAULT,
)
from ..sdk import DroneRLSDK
from ..types.rl import Hyperparameters


class HyperparameterPanel(tk.LabelFrame):
    """
    Panel with sliders and spinboxes for all 8 hyperparameters.

    **Input Data:** SDK reference; defaults from constants.py.
    **Output Data:** Hyperparameters dataclass via get_hyperparameters().
    **Setup Data:** ttk.Scale and ttk.Spinbox widgets built in __init__.
    """

    def __init__(
        self,
        parent: tk.Widget,
        sdk: DroneRLSDK,
        status_cb: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent, text="Hyperparameters", padx=4, pady=2)
        self._sdk = sdk
        self._status_cb = status_cb
        self._alpha_var = tk.DoubleVar(value=ALPHA_DEFAULT)
        self._gamma_var = tk.DoubleVar(value=GAMMA_DEFAULT)
        self._eps_var = tk.DoubleVar(value=EPSILON_DEFAULT)
        self._eps_decay_var = tk.DoubleVar(value=EPSILON_DECAY_DEFAULT)
        self._eps_min_var = tk.DoubleVar(value=EPSILON_MIN_DEFAULT)
        self._episodes_var = tk.IntVar(value=TOTAL_EPISODES_DEFAULT)
        self._max_steps_var = tk.IntVar(value=MAX_STEPS_DEFAULT)
        self._seed_var = tk.IntVar(value=RANDOM_SEED_DEFAULT)
        self._build()

    def _slider_row(self, label: str, var: tk.DoubleVar,
                    lo: float, hi: float, row: int) -> None:
        tk.Label(self, text=label, width=14, anchor=tk.E).grid(
            row=row, column=0, sticky=tk.E)
        tk.Scale(self, variable=var, from_=lo, to=hi, orient=tk.HORIZONTAL,
                 resolution=0.001, length=130,
                 showvalue=True).grid(row=row, column=1, sticky=tk.W)

    def _spin_row(self, label: str, var: tk.IntVar,
                  lo: int, hi: int, row: int) -> None:
        tk.Label(self, text=label, width=14, anchor=tk.E).grid(
            row=row, column=0, sticky=tk.E)
        ttk.Spinbox(self, textvariable=var, from_=lo, to=hi,
                    width=8).grid(row=row, column=1, sticky=tk.W)

    def _build(self) -> None:
        self._slider_row("α (learn rate)", self._alpha_var, 0.01, 1.0, 0)
        self._slider_row("γ (discount)", self._gamma_var, 0.0, 0.99, 1)
        self._slider_row("ε (explore)", self._eps_var, 0.0, 1.0, 2)
        self._slider_row("ε decay", self._eps_decay_var, 0.9, 1.0, 3)
        self._slider_row("ε min", self._eps_min_var, 0.001, 0.1, 4)
        self._spin_row("Episodes", self._episodes_var, 10, 10000, 5)
        self._spin_row("Max steps", self._max_steps_var, 10, 2000, 6)
        self._spin_row("Random seed", self._seed_var, 0, 99999, 7)

    def get_hyperparameters(self) -> Hyperparameters:
        """Build and return a Hyperparameters dataclass from current widget values."""
        return Hyperparameters(
            alpha=round(self._alpha_var.get(), 4),
            gamma=round(self._gamma_var.get(), 4),
            epsilon=round(self._eps_var.get(), 4),
            epsilon_decay=round(self._eps_decay_var.get(), 4),
            epsilon_min=round(self._eps_min_var.get(), 4),
            max_steps_per_episode=self._max_steps_var.get(),
            total_episodes=self._episodes_var.get(),
            random_seed=self._seed_var.get(),
        )

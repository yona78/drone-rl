"""DroneRLSDK — single entry point for all RL business logic (§4).

The GUI never imports from drone_rl.rl directly (§4 SDK boundary).
"""

from __future__ import annotations

import math
import threading

from ..rl.qtable import init_qtable
from ..types.grid import GridState
from ..types.rl import (
    EpisodeRecord,
    Hyperparameters,
    QTable,
    RewardConfig,
)
from ..utils import LAYOUTS_DIR, LOGS_DIR, POLICIES_DIR, create_rng
from .accessors import AccessorMixin
from .execution import ExecutionMixin
from .middleware import MiddlewareHost


class DroneRLSDK(MiddlewareHost, AccessorMixin, ExecutionMixin):
    """
    Single entry point for all RL business logic (§4 — Dr. Segal).

    **Input Data:** GridState, Hyperparameters, RewardConfig from GUI/config.
    **Output Data:** EpisodeRecord list, trained QTable, policy paths.
    **Setup Data:** RNG, middleware list, output dirs created in __init__.
    """

    def __init__(
        self,
        hp: Hyperparameters | None = None,
        rewards: RewardConfig | None = None,
    ) -> None:
        self._hp = hp or Hyperparameters()
        self._rewards = rewards or RewardConfig()
        self._rng = create_rng(self._hp.random_seed)
        self._grid: GridState | None = None
        self._qtable: QTable = {}
        self._records: list[EpisodeRecord] = []
        self._middleware: list = []
        self._pause_event = threading.Event()
        self._state_lock = threading.Lock()
        for d in (POLICIES_DIR, LOGS_DIR, LAYOUTS_DIR):
            d.mkdir(parents=True, exist_ok=True)
        self._validate_config()

    def _validate_config(self) -> None:
        hp = self._hp
        if not (0 < hp.alpha <= 1):
            raise ValueError(f"alpha must be in (0,1], got {hp.alpha}")
        if not (0 <= hp.gamma < 1):
            raise ValueError(f"gamma must be in [0,1), got {hp.gamma}")
        if not (0 <= hp.epsilon <= 1):
            raise ValueError(f"epsilon must be in [0,1], got {hp.epsilon}")
        for field_name in (
            "goal_reached",
            "empty_step",
            "building_collision",
            "trap_hit",
            "crosswind_penalty",
        ):
            v = getattr(self._rewards, field_name)
            if not math.isfinite(v):
                raise ValueError(f"reward.{field_name} must be finite")

    def create_environment(self, grid: GridState) -> None:
        """Set the active grid and re-initialise the Q-table."""
        self._grid = grid
        self._qtable = init_qtable(grid)

    def update_hyperparameters(self, hp: Hyperparameters) -> None:
        """Apply new hyperparameters and re-seed RNG (§6.2)."""
        self._hp = hp
        self._rng = create_rng(hp.random_seed)
        self._validate_config()

    def reset(self) -> None:
        """Reset Q-table, records, and RNG to initial state."""
        self._pause_event.clear()
        if self._grid:
            self._qtable = init_qtable(self._grid)
        self._records.clear()
        self._rng = create_rng(self._hp.random_seed)

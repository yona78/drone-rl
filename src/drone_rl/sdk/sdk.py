"""DroneRLSDK — single entry point for all RL business logic (§4).

The GUI never imports from drone_rl.rl directly (§4 SDK boundary).
"""

from __future__ import annotations

import math
import queue
import threading
from dataclasses import replace as dc_replace

from ..rl.episode import run_step
from ..rl.qtable import init_qtable
from ..types.agent import Action, AgentState, TerminalReason
from ..types.grid import GridState
from ..types.rl import (
    EpisodeRecord,
    Hyperparameters,
    QTable,
    RewardConfig,
)
from ..utils import LAYOUTS_DIR, LOGS_DIR, POLICIES_DIR, create_rng
from .accessors import AccessorMixin
from .middleware import MiddlewareHost


class DroneRLSDK(MiddlewareHost, AccessorMixin):
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

    def train(
        self,
        num_episodes: int | None = None,
        update_queue: queue.Queue | None = None,
    ) -> list[EpisodeRecord]:
        """Run training loop; emit EpisodeRecords to update_queue if given."""
        if self._grid is None:
            raise RuntimeError("Call create_environment() before train()")
        n = num_episodes or self._hp.total_episodes
        new_records: list[EpisodeRecord] = []
        for ep in range(n):
            if self._pause_event.is_set():
                break
            self._call_hook_before_episode_start(ep)
            agent = AgentState(
                position=self._grid.start_pos,
                accumulated_reward=0.0,
                step_count=0,
                is_done=False,
            )
            while not agent.is_done:
                agent, self._qtable = run_step(
                    agent,
                    self._grid,
                    self._qtable,
                    self._hp,
                    self._rewards,
                    self._rng,
                )
                self._call_hook_after_step_update(agent)
            reason = agent.terminal_reason or TerminalReason.MAX_STEPS
            record = EpisodeRecord(
                episode=ep,
                total_reward=agent.accumulated_reward,
                steps=agent.step_count,
                terminal_reason=reason,
                epsilon=self._hp.epsilon,
            )
            with self._state_lock:
                new_records.append(record)
                self._records.append(record)
                new_eps = max(self._hp.epsilon_min, self._hp.epsilon * self._hp.epsilon_decay)
                self._hp = dc_replace(self._hp, epsilon=new_eps)
            if update_queue is not None:
                update_queue.put_nowait(record)
            self._call_hook_on_episode_complete(record)
        return new_records

    def pause(self) -> None:
        """Signal training to pause after the current episode."""
        self._pause_event.set()
        self._call_hook_on_training_pause()

    def resume(self) -> None:
        """Clear pause flag; training can continue."""
        self._pause_event.clear()
        self._call_hook_on_training_resume()

    def reset(self) -> None:
        """Reset Q-table, records, and RNG to initial state."""
        self._pause_event.clear()
        if self._grid:
            self._qtable = init_qtable(self._grid)
        self._records.clear()
        self._rng = create_rng(self._hp.random_seed)

    def step(self, action: Action) -> tuple[AgentState, float, bool]:
        """Execute a single step in the current environment."""
        if self._grid is None:
            raise RuntimeError("Call create_environment() first")
        agent = AgentState(
            position=self._grid.start_pos,
            accumulated_reward=0.0,
            step_count=0,
            is_done=False,
        )
        new_agent, self._qtable = run_step(
            agent,
            self._grid,
            self._qtable,
            self._hp,
            self._rewards,
            self._rng,
        )
        return new_agent, new_agent.accumulated_reward, new_agent.is_done

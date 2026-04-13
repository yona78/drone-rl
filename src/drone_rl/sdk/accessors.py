"""
AccessorMixin — read-only queries and file I/O wrappers (§4).

Provides play_best_policy(), get_qtable(), get_episode_stats(),
and thin wrappers over sdk/io.py save/load/export helpers.

Concrete class must set: _grid, _qtable, _records.

Reference: CODE_PLAN section 14, Dr. Segal §4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..types.grid import GridState
from ..types.rl import QTable, state_key
from .io import (
    export_logs,
    load_layout,
    load_policy,
    save_experiment_results,
    save_layout,
    save_policy,
)


class AccessorMixin:
    """
    Mixin that exposes query and I/O operations.

    **Input Data:** _grid, _qtable, _records supplied by concrete class.
    **Output Data:** paths, policy/layout structs, stats dicts.
    **Setup Data:** delegates all I/O to sdk/io.py pure functions.
    """

    _grid: Any
    _qtable: QTable
    _records: list[Any]

    # --- Policy Evaluation ---

    def play_best_policy(self, max_steps: int = 200) -> list[tuple[int, int]]:
        """Traverse grid greedily (epsilon=0); return path as (row,col) list."""
        if self._grid is None:
            raise RuntimeError("Call create_environment() first")
        from ..rl.environment import apply_action
        from ..rl.qtable import best_action
        pos = self._grid.start_pos
        path = [(pos.row, pos.col)]
        visited: set[str] = {state_key(pos.row, pos.col)}
        for _ in range(max_steps):
            if pos == self._grid.goal_pos:
                break
            action = best_action(self._qtable, pos.row, pos.col)
            pos = apply_action(pos, action, self._grid)
            sk = state_key(pos.row, pos.col)
            if sk in visited:
                break  # cycle detected
            visited.add(sk)
            path.append((pos.row, pos.col))
        return path

    # --- Queries ---

    def get_qtable(self) -> dict:
        """Return serialised Q-table for GUI visualisation (thread-safe)."""
        from ..rl.qtable import qtable_to_dict
        lock = getattr(self, "_state_lock", None)
        if lock is not None:
            with lock:
                return qtable_to_dict(dict(self._qtable))
        return qtable_to_dict(self._qtable)

    def get_episode_stats(self) -> list[dict]:
        """Return list of episode stat dicts (thread-safe)."""
        lock = getattr(self, "_state_lock", None)
        records = list(self._records) if lock is None else self._locked_records(lock)
        return [
            {
                "episode": r.episode,
                "total_reward": r.total_reward,
                "steps": r.steps,
                "terminal_reason": r.terminal_reason.value,
                "epsilon": r.epsilon,
            }
            for r in records
        ]

    def _locked_records(self, lock: object) -> list:
        """Return a snapshot of _records under the state lock."""
        with lock:  # type: ignore[attr-defined]
            return list(self._records)

    # --- File I/O (thin wrappers over sdk/io.py) ---

    def save_policy(self, filepath: Path | str) -> None:
        """Save current Q-table to JSON."""
        save_policy(self._qtable, Path(filepath))

    def load_policy(self, filepath: Path | str) -> None:
        """Load Q-table from JSON."""
        self._qtable = load_policy(Path(filepath))

    def save_layout(self, filepath: Path | str) -> None:
        """Save current grid layout to JSON."""
        if self._grid is None:
            raise RuntimeError("No environment loaded")
        save_layout(self._grid, Path(filepath))

    def load_layout(self, filepath: Path | str) -> GridState:
        """Load grid layout from JSON and set as active environment."""
        grid = load_layout(Path(filepath))
        self.create_environment(grid)  # type: ignore[attr-defined]
        return grid

    def export_logs(self, filepath: Path | str) -> None:
        """Export episode records to CSV."""
        export_logs(self._records, Path(filepath))

    def save_results(self, filepath: Path | str, metadata: dict | None = None) -> None:
        """Save experiment summary + metadata to JSON (§7.4)."""
        save_experiment_results(
            self._records, metadata or {}, Path(filepath)
        )

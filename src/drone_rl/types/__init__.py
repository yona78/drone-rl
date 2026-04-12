"""
Canonical dataclasses — no business logic.

All shared types for the drone-rl application are exported here.
"""

from .agent import ALL_ACTIONS, Action, AgentState, TerminalReason
from .grid import Cell, CellType, Coordinate, GridState
from .rl import (
    EpisodeRecord,
    Hyperparameters,
    QTable,
    RewardConfig,
    StateKey,
    state_key,
)

__all__ = [
    "Action",
    "AgentState",
    "ALL_ACTIONS",
    "Cell",
    "CellType",
    "Coordinate",
    "EpisodeRecord",
    "GridState",
    "Hyperparameters",
    "QTable",
    "RewardConfig",
    "StateKey",
    "state_key",
    "TerminalReason",
]

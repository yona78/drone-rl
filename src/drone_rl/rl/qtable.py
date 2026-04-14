"""
Q-Table management for the 2D Drone Pathfinding RL simulation.

Provides pure functions for initializing, querying, and updating
the tabular Q-table. Keys are Action enum members, NOT strings.

Reference: CODE_PLAN section 3.3 (Review Point #1).
"""

from __future__ import annotations

import json
from typing import Any

from ..types.agent import ALL_ACTIONS, Action
from ..types.grid import CellType, GridState
from ..types.rl import QTable, state_key


def init_qtable(grid: GridState) -> QTable:
    """
    Initialize Q-table for all walkable cells with Q(s,a) = 0.0.

    Building cells are excluded — the agent can never occupy them.
    Keys are Action enum members (Review Point #1).
    """
    table: QTable = {}
    for r in range(grid.rows):
        for c in range(grid.cols):
            if grid.get_cell_type(r, c) != CellType.BUILDING:
                sk = state_key(r, c)
                table[sk] = dict.fromkeys(ALL_ACTIONS, 0.0)
    return table


def get_q(table: QTable, row: int, col: int, action: Action) -> float:
    """Get Q-value; returns 0.0 if state or action not present."""
    sk = state_key(row, col)
    return table.get(sk, {}).get(action, 0.0)


def set_q(
    table: QTable,
    row: int,
    col: int,
    action: Action,
    value: float,
) -> QTable:
    """Set Q-value, creating state entry if needed. Mutates in place."""
    sk = state_key(row, col)
    if sk not in table:
        table[sk] = dict.fromkeys(ALL_ACTIONS, 0.0)
    table[sk][action] = value
    return table


def best_action(table: QTable, row: int, col: int) -> Action:
    """Return action with highest Q-value (argmax). Ties broken by enum order."""
    sk = state_key(row, col)
    entries = table.get(sk, dict.fromkeys(ALL_ACTIONS, 0.0))
    return max(ALL_ACTIONS, key=lambda a: entries.get(a, 0.0))


def max_q(table: QTable, row: int, col: int) -> float:
    """Return maximum Q-value across all actions for a state."""
    sk = state_key(row, col)
    entries = table.get(sk, {})
    if not entries:
        return 0.0
    return max(entries.values())


def qtable_to_dict(table: QTable) -> dict[str, dict[str, float]]:
    """Serialize QTable to JSON-compatible dict (Action enum → string)."""
    return {sk: {a.value: v for a, v in actions.items()} for sk, actions in table.items()}


def qtable_from_dict(data: dict[str, Any]) -> QTable:
    """Deserialize QTable from JSON-compatible dict (string → Action enum)."""
    action_map = {a.value: a for a in Action}
    table: QTable = {}
    for sk, actions in data.items():
        if not isinstance(actions, dict):
            raise ValueError(
                f"Invalid Q-table format: value for state '{sk}' is not a dictionary. "
                "Are you sure this is a policy file and not a layout file?"
            )
        table[sk] = {}
        for k, v in actions.items():
            if k not in action_map:
                continue  # Skip metadata or invalid actions
            table[sk][action_map[k]] = float(v)
    return table


def qtable_to_json(table: QTable) -> str:
    """Serialize QTable to JSON string."""
    return json.dumps(qtable_to_dict(table), indent=2)


def qtable_from_json(text: str) -> QTable:
    """Deserialize QTable from JSON string."""
    return qtable_from_dict(json.loads(text))

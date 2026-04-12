"""
Epsilon-greedy action selection for the 2D Drone Pathfinding RL simulation.

All randomness uses a local random.Random instance, NEVER global
random.seed(). This ensures deterministic reproducibility without
polluting global state (section 8.1).

Reference: CODE_PLAN section 10.
"""

from __future__ import annotations

import random as _random_module

from ..types.agent import ALL_ACTIONS, Action
from ..types.rl import QTable
from .qtable import best_action


def select_action(
    table: QTable,
    row: int,
    col: int,
    epsilon: float,
    rng: _random_module.Random,
) -> Action:
    """
    Epsilon-greedy action selection using local RNG.

    With probability epsilon, explore (random action via local RNG).
    Otherwise, exploit (best action from Q-table).

    Input Data: Q-table, state (row,col), epsilon, local RNG.
    Output Data: Action enum member.

    Critical: ``rng`` MUST be a local ``random.Random(seed)`` instance,
    NOT the global ``random`` module (Review Point #3).
    """
    if rng.random() < epsilon:
        return rng.choice(ALL_ACTIONS)
    return best_action(table, row, col)

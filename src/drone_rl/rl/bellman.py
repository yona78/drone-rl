"""
Bellman update engine for the 2D Drone Pathfinding RL simulation.

Implements the core Q-Learning update rule as a pure function.

Reference: PRD section 5.3, CODE_PLAN section 7.
  Q(s,a) <- Q(s,a) + alpha * [R(s,a) + gamma * max_a' Q(s',a') - Q(s,a)]
"""

from __future__ import annotations

from ..types.agent import Action
from ..types.rl import Hyperparameters, QTable
from .qtable import get_q, max_q, set_q


def bellman_update(
    table: QTable,
    row: int,
    col: int,
    action: Action,
    reward: float,
    next_row: int,
    next_col: int,
    is_done: bool,
    hp: Hyperparameters,
) -> QTable:
    """
    Apply the Bellman equation Q-Learning update (PRD section 5.3).

    Q(s,a) <- Q(s,a) + alpha * [R(s,a) + gamma * max_a' Q(s',a') - Q(s,a)]

    If the episode is done (terminal state), future Q-value is 0.

    Input Data: Q-table, current state (row,col), action taken, reward,
                next state (next_row,next_col), terminal flag, hyperparams.
    Output Data: Updated Q-table (mutated in place).
    """
    current_q = get_q(table, row, col, action)

    # Terminal states have no future value
    future_q = 0.0 if is_done else max_q(table, next_row, next_col)

    # TD target and error
    td_target = reward + hp.gamma * future_q
    td_error = td_target - current_q

    # Q-value update
    new_q = current_q + hp.alpha * td_error

    return set_q(table, row, col, action, new_q)

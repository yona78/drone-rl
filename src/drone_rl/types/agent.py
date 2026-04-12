"""
Agent and action types for the 2D Drone Pathfinding RL simulation.

Defines movement actions, terminal reasons, and agent runtime state.

Reference: CODE_PLAN section 3.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .grid import Coordinate


class Action(Enum):
    """
    Cardinal movement actions.

    UP decreases row, DOWN increases row,
    LEFT decreases col, RIGHT increases col.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


ALL_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
"""All four cardinal actions in a stable order."""


class TerminalReason(Enum):
    """How an episode ended."""

    GOAL_REACHED = "goal_reached"
    TRAP_HIT = "trap_hit"
    MAX_STEPS = "max_steps"


@dataclass
class AgentState:
    """
    Runtime agent snapshot.

    Tracks the agent's current position, accumulated reward,
    step count, and whether the episode has terminated.
    """

    position: Coordinate
    accumulated_reward: float
    step_count: int
    is_done: bool
    terminal_reason: TerminalReason | None = None

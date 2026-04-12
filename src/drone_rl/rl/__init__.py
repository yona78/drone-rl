"""
Pure RL engine — zero tkinter imports.

All RL logic is accessed as pure functions. The OOP wrappers in base.py
provide the class hierarchy required by Dr. Segal guidelines.
"""

from .base import BaseEnvironment, GridEnvironment, RewardMixin
from .bellman import bellman_update
from .environment import apply_action
from .episode import run_episode, run_step
from .policy import select_action
from .qtable import (
    best_action,
    get_q,
    init_qtable,
    max_q,
    qtable_from_dict,
    qtable_from_json,
    qtable_to_dict,
    qtable_to_json,
    set_q,
)
from .rewards import compute_reward

__all__ = [
    "BaseEnvironment",
    "GridEnvironment",
    "RewardMixin",
    "apply_action",
    "bellman_update",
    "best_action",
    "compute_reward",
    "get_q",
    "init_qtable",
    "max_q",
    "qtable_from_dict",
    "qtable_from_json",
    "qtable_to_dict",
    "qtable_to_json",
    "run_episode",
    "run_step",
    "select_action",
    "set_q",
]

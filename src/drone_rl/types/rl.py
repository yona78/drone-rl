"""
Q-Learning types for the 2D Drone Pathfinding RL simulation.

Defines the Q-table type alias, state key builder, hyperparameters,
reward configuration, and episode records.

Reference: CODE_PLAN section 3.3, PRD sections 4.1-4.2.
"""

from __future__ import annotations

from dataclasses import dataclass

from .agent import Action, TerminalReason

# Q-Table: Maps "row,col" -> {Action enum -> Q-value}
StateKey = str
"""Canonical state key format: ``"row,col"``."""

QTable = dict[StateKey, dict[Action, float]]
"""Keys are Action enum members, NOT strings (Review Point #1)."""


def state_key(row: int, col: int) -> StateKey:
    """
    Build a canonical state key string.

    Always use this function — never build state keys manually.
    """
    return f"{row},{col}"


@dataclass
class Hyperparameters:
    """
    Learning configuration (PRD section 4.2).

    Input Data: All hyperparameter values.
    Output Data: Used by RL engine for training.
    """

    alpha: float = 0.1
    gamma: float = 0.99
    epsilon: float = 1.0
    epsilon_decay: float = 0.995
    epsilon_min: float = 0.01
    max_steps_per_episode: int = 500
    total_episodes: int = 1000
    random_seed: int = 42


@dataclass
class RewardConfig:
    """
    Exact reward values (PRD section 4.1 — MANDATORY).

    These values must match config/rewards.json exactly.
    """

    goal_reached: float = 100.0
    empty_step: float = -1.0
    building_collision: float = -10.0
    trap_hit: float = -100.0
    crosswind_penalty: float = -10.0


@dataclass
class EpisodeRecord:
    """Training history per episode."""

    episode: int
    total_reward: float
    steps: int
    terminal_reason: TerminalReason
    epsilon: float

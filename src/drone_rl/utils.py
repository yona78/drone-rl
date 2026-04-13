"""
Helper functions for the 2D Drone Pathfinding RL simulation.

Provides path resolution, RNG creation, and small math utilities.
All functions are pure (no side effects) except path constants.

Reference: CODE_PLAN section 3.5, Phase 1 spec.
"""

from __future__ import annotations

import random
from pathlib import Path

# --- Path Constants (§14.3 — pathlib, never hardcoded) ---

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
"""Resolves to the drone-rl/ project root directory."""

CONFIG_DIR: Path = PROJECT_ROOT / "config"
"""Path to config/ directory containing JSON configuration files."""

POLICIES_DIR: Path = PROJECT_ROOT / "policies"
"""Path to policies/ directory for saved Q-tables."""

LOGS_DIR: Path = PROJECT_ROOT / "logs"
"""Path to logs/ directory for episode CSV logs."""

LAYOUTS_DIR: Path = PROJECT_ROOT / "layouts"
"""Path to layouts/ directory for saved grid layouts."""


def create_rng(seed: int) -> random.Random:
    """
    Create a LOCAL Random instance seeded deterministically.

    NEVER use global ``random.seed()`` — always use this function
    to get a local RNG instance for reproducibility.

    Input Data: integer seed.
    Output Data: ``random.Random`` instance.
    """
    return random.Random(seed)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to [min_val, max_val] range.

    Input Data: value, lower bound, upper bound.
    Output Data: clamped float.
    """
    return max(min_val, min(value, max_val))


def is_valid_coordinate(
    row: int,
    col: int,
    grid_rows: int,
    grid_cols: int,
) -> bool:
    """
    Check if (row, col) is within grid bounds.

    Input Data: row, col, grid dimensions.
    Output Data: True if in bounds.
    """
    return 0 <= row < grid_rows and 0 <= col < grid_cols


def manhattan_distance(r1: int, c1: int, r2: int, c2: int) -> int:
    """
    Compute Manhattan distance between two grid positions.

    Input Data: two (row, col) pairs.
    Output Data: non-negative integer distance.
    """
    return abs(r1 - r2) + abs(c1 - c2)


def epsilon_decay(epsilon: float, decay_rate: float) -> float:
    """
    Apply multiplicative epsilon decay.

    Input Data: current epsilon, decay rate.
    Output Data: decayed epsilon (always >= 0).
    """
    return max(0.0, epsilon * decay_rate)

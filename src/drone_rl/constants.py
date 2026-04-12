"""
Immutable project constants for the 2D Drone Pathfinding RL simulation.

Contains color mappings, grid limits, hyperparameter defaults, and reward
values. All values here serve as fallback defaults; runtime values come
from config/ JSON files via ConfigManager.

Reference: CODE_PLAN section 3.5, PRD sections 4.1-4.2.
"""

from .types.grid import CellType

# --- Grid Dimensions ---

GRID_WIDTH_DEFAULT = 10
GRID_HEIGHT_DEFAULT = 10
GRID_WIDTH_MAX = 20
GRID_HEIGHT_MAX = 20

# --- Hyperparameter Defaults (PRD §4.2) ---

ALPHA_DEFAULT = 0.1
"""Learning rate."""

GAMMA_DEFAULT = 0.99
"""Discount factor."""

EPSILON_DEFAULT = 1.0
"""Initial exploration rate."""

EPSILON_DECAY_DEFAULT = 0.995
"""Multiplicative decay per episode."""

EPSILON_MIN_DEFAULT = 0.01
"""Floor for epsilon."""

MAX_STEPS_DEFAULT = 500
"""Maximum steps per episode."""

TOTAL_EPISODES_DEFAULT = 1000
"""Default number of training episodes."""

RANDOM_SEED_DEFAULT = 42
"""Default RNG seed for reproducibility."""

# --- Reward Schedule (PRD §4.1 — MANDATORY) ---

REWARD_GOAL = 100.0
REWARD_STEP = -1.0
REWARD_BUILDING_COLLISION = -10.0
REWARD_TRAP_HIT = -100.0
REWARD_CROSSWIND = -10.0

# --- Cell Colors (tkinter-compatible) ---

COLOR_EMPTY = "white"
COLOR_START = "green"
COLOR_GOAL = "gold"
COLOR_BUILDING = "gray"
COLOR_TRAP = "red"
COLOR_CROSSWIND = "blue"

CELL_COLORS: dict[CellType, str] = {
    CellType.EMPTY: COLOR_EMPTY,
    CellType.START: COLOR_START,
    CellType.GOAL: COLOR_GOAL,
    CellType.BUILDING: COLOR_BUILDING,
    CellType.TRAP: COLOR_TRAP,
    CellType.CROSSWIND: COLOR_CROSSWIND,
}
"""Maps each CellType to its display color."""

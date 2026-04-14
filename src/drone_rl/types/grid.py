"""
Grid & environment types for the 2D Drone Pathfinding RL simulation.

Defines the cell types, coordinates, and grid state used throughout the
application. All types are dataclasses with no business logic.

Reference: PRD section 2.4 (Obstacle Catalog), CODE_PLAN section 3.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Action


class CellType(Enum):
    """
    Obstacle types from PRD section 2.4.

    Each member maps to a color and reward value defined in constants.py
    and config/rewards.json respectively.
    """

    EMPTY = "empty"  # White  — default walkable tile
    START = "start"  # Green  — drone starting position
    GOAL = "goal"  # Gold   — target destination, +100 reward
    BUILDING = "building"  # Gray   — blocks movement, -10 penalty
    TRAP = "trap"  # Red    — ends episode, -100 penalty
    CROSSWIND = "crosswind"  # Blue   — alters movement, -10 penalty


@dataclass(frozen=True)
class Coordinate:
    """Immutable 2D grid coordinate.

    Input Data: row (int), col (int).
    Output Data: string representation "(row, col)".
    Setup Data: none — frozen dataclass, no configuration.
    """

    row: int
    col: int

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"


@dataclass(frozen=True)
class Cell:
    """Immutable single grid tile value object."""

    row: int
    col: int
    type: CellType


@dataclass
class GridState:
    """
    Full environment state for the grid world.

    Input Data: rows, cols, cells dict, start/goal positions.
    Output Data: cell lookups, wind direction queries.
    Setup Data: wind_directions for crosswind tiles.
    """

    rows: int
    cols: int
    cells: dict[tuple[int, int], CellType]
    start_pos: Coordinate
    goal_pos: Coordinate
    wind_directions: dict[tuple[int, int], Action] = field(
        default_factory=dict,
    )

    def get_cell_type(self, row: int, col: int) -> CellType:
        """Lookup cell type; check for start/goal, then default to EMPTY."""
        if row == self.start_pos.row and col == self.start_pos.col:
            return CellType.START
        if row == self.goal_pos.row and col == self.goal_pos.col:
            return CellType.GOAL
        return self.cells.get((row, col), CellType.EMPTY)

    def get_wind_direction(self, row: int, col: int) -> Action:
        """
        Lookup wind direction for a crosswind tile.

        Returns the configured direction, or Action.UP as default.
        """
        from .agent import Action as _Action

        return self.wind_directions.get((row, col), _Action.UP)

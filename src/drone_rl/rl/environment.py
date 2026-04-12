"""
Environment simulation for the 2D Drone Pathfinding RL simulation.

Implements movement physics as a pure function: boundary checks,
building collisions, and crosswind drift with per-tile configurable
wind direction and drift cancellation at boundaries/buildings.

Reference: CODE_PLAN section 9, PRD section 3.4.
"""

from __future__ import annotations

from ..types.agent import Action
from ..types.grid import CellType, Coordinate, GridState
from ..utils import is_valid_coordinate

# Movement deltas: Action -> (delta_row, delta_col)
DELTAS: dict[Action, tuple[int, int]] = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}


def apply_action(
    pos: Coordinate,
    action: Action,
    grid: GridState,
) -> Coordinate:
    """
    Apply movement physics and return the resulting position.

    Movement rules:
    1. Compute candidate position from action delta.
    2. If candidate is out-of-bounds -> stay (return current pos).
    3. If candidate is a Building -> stay (blocked).
    4. If candidate is a Crosswind tile:
       a. Get per-tile wind direction via grid.get_wind_direction().
       b. Compute drift target = candidate + wind delta.
       c. If drift target is out-of-bounds or a Building,
          cancel drift — drone stays on crosswind tile.
          (PRD section 3.4: drift cancellation)
       d. Otherwise, drone lands on drift target.
    5. Otherwise -> move to candidate.

    Input Data: current position, action, grid state.
    Output Data: new Coordinate after physics applied.
    """
    dr, dc = DELTAS[action]
    next_r, next_c = pos.row + dr, pos.col + dc

    # Boundary check
    if not is_valid_coordinate(next_r, next_c, grid.rows, grid.cols):
        return pos

    # Building check — movement blocked
    cell_type = grid.get_cell_type(next_r, next_c)
    if cell_type == CellType.BUILDING:
        return pos

    # Crosswind drift physics
    if cell_type == CellType.CROSSWIND:
        wind_dir = grid.get_wind_direction(next_r, next_c)
        wd_r, wd_c = DELTAS[wind_dir]
        drift_r, drift_c = next_r + wd_r, next_c + wd_c

        # Drift cancellation: OOB or building -> stay on crosswind tile
        if not is_valid_coordinate(drift_r, drift_c, grid.rows, grid.cols):
            return Coordinate(next_r, next_c)
        if grid.get_cell_type(drift_r, drift_c) == CellType.BUILDING:
            return Coordinate(next_r, next_c)

        return Coordinate(drift_r, drift_c)

    return Coordinate(next_r, next_c)

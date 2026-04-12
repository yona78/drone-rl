"""Shared pytest fixtures for the drone-rl test suite."""

import pytest

from drone_rl.types.agent import Action
from drone_rl.types.grid import CellType, Coordinate, GridState


@pytest.fixture()
def small_grid() -> GridState:
    """A minimal 5x5 grid with start at (0,0) and goal at (4,4)."""
    return GridState(
        rows=5,
        cols=5,
        cells={},
        start_pos=Coordinate(row=0, col=0),
        goal_pos=Coordinate(row=4, col=4),
    )


@pytest.fixture()
def grid_with_obstacles() -> GridState:
    """5x5 grid with one of each obstacle type."""
    return GridState(
        rows=5,
        cols=5,
        cells={
            (1, 1): CellType.BUILDING,
            (2, 2): CellType.TRAP,
            (3, 3): CellType.CROSSWIND,
        },
        start_pos=Coordinate(row=0, col=0),
        goal_pos=Coordinate(row=4, col=4),
        wind_directions={(3, 3): Action.RIGHT},
    )

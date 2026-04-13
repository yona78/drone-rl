"""Unit tests for drone_rl.rl.environment module — movement physics."""

from drone_rl.rl.environment import apply_action
from drone_rl.types.agent import Action
from drone_rl.types.grid import CellType, Coordinate, GridState


def _grid(
    rows: int = 5,
    cols: int = 5,
    cells: dict | None = None,
    wind: dict | None = None,
) -> GridState:
    return GridState(
        rows=rows,
        cols=cols,
        cells=cells or {},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(rows - 1, cols - 1),
        wind_directions=wind or {},
    )


class TestValidMoves:
    """Movement on empty tiles."""

    def test_apply_action_valid_move_all_directions(self) -> None:
        grid = _grid()
        pos = Coordinate(2, 2)
        assert apply_action(pos, Action.UP, grid) == Coordinate(1, 2)
        assert apply_action(pos, Action.DOWN, grid) == Coordinate(3, 2)
        assert apply_action(pos, Action.LEFT, grid) == Coordinate(2, 1)
        assert apply_action(pos, Action.RIGHT, grid) == Coordinate(2, 3)

    def test_apply_action_goal_cell_reachable(self) -> None:
        grid = _grid()
        pos = Coordinate(3, 4)
        result = apply_action(pos, Action.DOWN, grid)
        assert result == Coordinate(4, 4)  # goal


class TestBoundaryBlocking:
    """Agent stays put at grid edges."""

    def test_apply_action_boundary_check_up(self) -> None:
        assert apply_action(Coordinate(0, 2), Action.UP, _grid()) == Coordinate(0, 2)

    def test_apply_action_boundary_check_down(self) -> None:
        assert apply_action(Coordinate(4, 2), Action.DOWN, _grid()) == Coordinate(4, 2)

    def test_apply_action_boundary_check_left(self) -> None:
        assert apply_action(Coordinate(2, 0), Action.LEFT, _grid()) == Coordinate(2, 0)

    def test_apply_action_boundary_check_right(self) -> None:
        assert apply_action(Coordinate(2, 4), Action.RIGHT, _grid()) == Coordinate(2, 4)

    def test_apply_action_blocked_by_boundary(self) -> None:
        pos = Coordinate(0, 0)
        assert apply_action(pos, Action.UP, _grid()) == pos
        assert apply_action(pos, Action.LEFT, _grid()) == pos


class TestBuildingBlocking:
    """Agent cannot enter building tiles."""

    def test_apply_action_blocked_by_building(self) -> None:
        grid = _grid(cells={(1, 1): CellType.BUILDING})
        pos = Coordinate(0, 1)
        result = apply_action(pos, Action.DOWN, grid)
        assert result == pos  # blocked


class TestCrosswindPhysics:
    """Crosswind drift with per-tile configurable direction."""

    def test_crosswind_drift_in_configured_direction(self) -> None:
        grid = _grid(
            cells={(2, 2): CellType.CROSSWIND},
            wind={(2, 2): Action.RIGHT},
        )
        pos = Coordinate(1, 2)
        result = apply_action(pos, Action.DOWN, grid)
        assert result == Coordinate(2, 3)  # landed on crosswind, drifted right

    def test_crosswind_drift_cancelled_at_boundary(self) -> None:
        grid = _grid(
            cells={(2, 4): CellType.CROSSWIND},
            wind={(2, 4): Action.RIGHT},
        )
        pos = Coordinate(1, 4)
        result = apply_action(pos, Action.DOWN, grid)
        assert result == Coordinate(2, 4)  # drift cancelled, stay on crosswind

    def test_crosswind_drift_cancelled_into_building(self) -> None:
        grid = _grid(
            cells={(2, 2): CellType.CROSSWIND, (2, 3): CellType.BUILDING},
            wind={(2, 2): Action.RIGHT},
        )
        pos = Coordinate(1, 2)
        result = apply_action(pos, Action.DOWN, grid)
        assert result == Coordinate(2, 2)  # drift into building cancelled

    def test_crosswind_different_wind_directions(self) -> None:
        for wind_dir, expected in [
            (Action.UP, Coordinate(1, 2)),
            (Action.DOWN, Coordinate(3, 2)),
            (Action.LEFT, Coordinate(2, 1)),
            (Action.RIGHT, Coordinate(2, 3)),
        ]:
            grid = _grid(
                cells={(2, 2): CellType.CROSSWIND},
                wind={(2, 2): wind_dir},
            )
            result = apply_action(Coordinate(1, 2), Action.DOWN, grid)
            assert result == expected, f"Wind {wind_dir} failed"

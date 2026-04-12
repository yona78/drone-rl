"""Unit tests for drone_rl.types.grid module."""

import pytest

from drone_rl.types.agent import Action
from drone_rl.types.grid import Cell, CellType, Coordinate, GridState


class TestCellType:
    """Tests for CellType enum."""

    def test_celltype_enum_values(self) -> None:
        assert CellType.EMPTY.value == "empty"
        assert CellType.START.value == "start"
        assert CellType.GOAL.value == "goal"
        assert CellType.BUILDING.value == "building"
        assert CellType.TRAP.value == "trap"
        assert CellType.CROSSWIND.value == "crosswind"

    def test_celltype_has_six_members(self) -> None:
        assert len(CellType) == 6


class TestCoordinate:
    """Tests for Coordinate dataclass."""

    def test_coordinate_equality(self) -> None:
        assert Coordinate(row=1, col=2) == Coordinate(row=1, col=2)

    def test_coordinate_inequality(self) -> None:
        assert Coordinate(row=1, col=2) != Coordinate(row=3, col=4)

    def test_coordinate_is_hashable(self) -> None:
        c = Coordinate(row=1, col=2)
        assert hash(c) == hash(Coordinate(row=1, col=2))
        assert {c: "test"}[Coordinate(row=1, col=2)] == "test"

    def test_coordinate_is_immutable(self) -> None:
        c = Coordinate(row=1, col=2)
        with pytest.raises(AttributeError):
            c.row = 5  # type: ignore[misc]

    def test_coordinate_str(self) -> None:
        assert str(Coordinate(row=3, col=7)) == "(3, 7)"


class TestCell:
    """Tests for Cell dataclass."""

    def test_cell_creation(self) -> None:
        cell = Cell(row=0, col=0, type=CellType.START)
        assert cell.row == 0
        assert cell.col == 0
        assert cell.type == CellType.START

    def test_cell_is_frozen(self) -> None:
        cell = Cell(row=0, col=0, type=CellType.EMPTY)
        with pytest.raises(AttributeError):
            cell.type = CellType.GOAL  # type: ignore[misc]


class TestGridState:
    """Tests for GridState dataclass."""

    def test_gridstate_creation(self, small_grid: GridState) -> None:
        assert small_grid.rows == 5
        assert small_grid.cols == 5

    def test_gridstate_get_cell_type_empty_default(
        self, small_grid: GridState,
    ) -> None:
        assert small_grid.get_cell_type(2, 2) == CellType.EMPTY

    def test_gridstate_get_cell_type_explicit(self) -> None:
        grid = GridState(
            rows=3, cols=3,
            cells={(1, 1): CellType.BUILDING},
            start_pos=Coordinate(0, 0),
            goal_pos=Coordinate(2, 2),
        )
        assert grid.get_cell_type(1, 1) == CellType.BUILDING

    def test_gridstate_set_cell_type(self, small_grid: GridState) -> None:
        small_grid.cells[(0, 1)] = CellType.TRAP
        assert small_grid.get_cell_type(0, 1) == CellType.TRAP

    def test_gridstate_start_and_goal_positions(
        self, small_grid: GridState,
    ) -> None:
        assert small_grid.start_pos == Coordinate(row=0, col=0)
        assert small_grid.goal_pos == Coordinate(row=4, col=4)

    def test_gridstate_wind_directions_default_empty(
        self, small_grid: GridState,
    ) -> None:
        assert small_grid.wind_directions == {}

    def test_gridstate_get_wind_direction_returns_configured(
        self, grid_with_obstacles: GridState,
    ) -> None:
        assert grid_with_obstacles.get_wind_direction(3, 3) == Action.RIGHT

    def test_gridstate_get_wind_direction_defaults_to_up(
        self, small_grid: GridState,
    ) -> None:
        assert small_grid.get_wind_direction(0, 0) == Action.UP

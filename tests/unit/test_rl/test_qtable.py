"""Unit tests for drone_rl.rl.qtable module."""

from drone_rl.rl.qtable import (
    best_action,
    get_q,
    init_qtable,
    max_q,
    qtable_from_dict,
    qtable_to_dict,
    set_q,
)
from drone_rl.types.agent import Action
from drone_rl.types.grid import CellType, Coordinate, GridState


def _make_grid() -> GridState:
    return GridState(
        rows=3,
        cols=3,
        cells={(1, 1): CellType.BUILDING},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(2, 2),
    )


class TestInitQtable:
    """Tests for init_qtable()."""

    def test_qtable_initialization(self) -> None:
        grid = _make_grid()
        qt = init_qtable(grid)
        # 9 cells minus 1 building = 8 states
        assert len(qt) == 8
        assert "1,1" not in qt  # building excluded

    def test_qtable_all_values_zero(self) -> None:
        grid = _make_grid()
        qt = init_qtable(grid)
        for actions in qt.values():
            for v in actions.values():
                assert v == 0.0

    def test_qtable_keys_are_action_enum(self) -> None:
        grid = _make_grid()
        qt = init_qtable(grid)
        for actions in qt.values():
            for key in actions:
                assert isinstance(key, Action)


class TestGetSetQ:
    """Tests for get_q() and set_q()."""

    def test_qtable_get_uninitialized_returns_zero(self) -> None:
        qt = {}
        assert get_q(qt, 99, 99, Action.UP) == 0.0

    def test_qtable_set_and_get(self) -> None:
        qt = {}
        set_q(qt, 0, 0, Action.UP, 5.5)
        assert get_q(qt, 0, 0, Action.UP) == 5.5

    def test_set_creates_entry(self) -> None:
        qt = {}
        set_q(qt, 3, 4, Action.LEFT, 1.0)
        assert "3,4" in qt
        assert get_q(qt, 3, 4, Action.LEFT) == 1.0


class TestBestAction:
    """Tests for best_action() and max_q()."""

    def test_qtable_get_best_action(self) -> None:
        qt = {}
        set_q(qt, 0, 0, Action.RIGHT, 10.0)
        set_q(qt, 0, 0, Action.UP, 2.0)
        assert best_action(qt, 0, 0) == Action.RIGHT

    def test_qtable_get_best_value(self) -> None:
        qt = {}
        set_q(qt, 0, 0, Action.DOWN, 7.5)
        set_q(qt, 0, 0, Action.LEFT, 3.0)
        assert max_q(qt, 0, 0) == 7.5

    def test_max_q_empty_returns_zero(self) -> None:
        assert max_q({}, 0, 0) == 0.0


class TestSerialization:
    """Tests for qtable_to_dict/qtable_from_dict."""

    def test_qtable_serialization_and_deserialization(self) -> None:
        qt = {}
        set_q(qt, 0, 0, Action.UP, 1.5)
        set_q(qt, 0, 0, Action.DOWN, -2.0)

        serialized = qtable_to_dict(qt)
        assert isinstance(serialized["0,0"]["up"], float)

        restored = qtable_from_dict(serialized)
        assert get_q(restored, 0, 0, Action.UP) == 1.5
        assert get_q(restored, 0, 0, Action.DOWN) == -2.0

    def test_qtable_from_dict_validation(self) -> None:
        import pytest
        # Layout-like format (int instead of dict)
        invalid = {"0,0": 5}
        with pytest.raises(ValueError, match="Invalid Q-table format"):
            qtable_from_dict(invalid)

"""Unit tests for drone_rl.rl.base module — OOP wrappers."""

import random

import pytest

from drone_rl.rl.base import BaseEnvironment, GridEnvironment, RewardMixin
from drone_rl.rl.rewards import compute_reward
from drone_rl.types.agent import Action, AgentState
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import RewardConfig


def _grid() -> GridState:
    return GridState(
        rows=5,
        cols=5,
        cells={(2, 2): CellType.TRAP},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(4, 4),
    )


class TestRewardMixin:
    """Tests for RewardMixin."""

    def test_reward_mixin_delegates_to_compute_reward(self) -> None:
        class Host(RewardMixin):
            pass

        h = Host()
        h._reward_config = RewardConfig()
        result = h.get_reward(CellType.EMPTY)
        expected = compute_reward(CellType.EMPTY, RewardConfig())
        assert result == expected


class TestBaseEnvironment:
    """Tests for BaseEnvironment ABC."""

    def test_base_environment_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            BaseEnvironment()  # type: ignore[abstract]


class TestGridEnvironment:
    """Tests for GridEnvironment concrete class."""

    def test_grid_environment_inherits_both(self) -> None:
        env = GridEnvironment(_grid(), RewardConfig(), random.Random(42))
        assert isinstance(env, RewardMixin)
        assert isinstance(env, BaseEnvironment)

    def test_grid_environment_validate_config_raises_on_invalid_dims(
        self,
    ) -> None:
        bad_grid = GridState(
            rows=0,
            cols=5,
            cells={},
            start_pos=Coordinate(0, 0),
            goal_pos=Coordinate(4, 4),
        )
        with pytest.raises(ValueError, match="dimensions"):
            GridEnvironment(bad_grid, RewardConfig(), random.Random(42))

    def test_grid_environment_validate_config_raises_on_same_start_goal(
        self,
    ) -> None:
        bad_grid = GridState(
            rows=5,
            cols=5,
            cells={},
            start_pos=Coordinate(0, 0),
            goal_pos=Coordinate(0, 0),
        )
        with pytest.raises(ValueError, match="Start and goal"):
            GridEnvironment(bad_grid, RewardConfig(), random.Random(42))

    def test_grid_environment_reset_returns_start_state(self) -> None:
        env = GridEnvironment(_grid(), RewardConfig(), random.Random(42))
        state = env.reset()
        assert isinstance(state, AgentState)
        assert state.position == Coordinate(0, 0)
        assert state.step_count == 0
        assert state.is_done is False

    def test_grid_environment_step_delegates_to_apply_action(self) -> None:
        env = GridEnvironment(_grid(), RewardConfig(), random.Random(42))
        env.reset()
        state, reward, is_done = env.step(Action.DOWN)
        assert isinstance(state, AgentState)
        assert state.position == Coordinate(1, 0)
        assert reward == -1.0  # empty step
        assert is_done is False

    def test_grid_environment_step_before_reset_raises(self) -> None:
        env = GridEnvironment(_grid(), RewardConfig(), random.Random(42))
        with pytest.raises(RuntimeError, match="reset"):
            env.step(Action.UP)

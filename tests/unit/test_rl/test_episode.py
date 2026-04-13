"""Unit tests for drone_rl.rl.episode module — step and episode execution."""

import random

from drone_rl.rl.episode import run_episode, run_step
from drone_rl.rl.qtable import init_qtable, set_q
from drone_rl.types.agent import Action, AgentState, TerminalReason
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import EpisodeRecord, Hyperparameters, RewardConfig


def _simple_grid() -> GridState:
    """2x2 grid: start (0,0), goal (1,1)."""
    return GridState(
        rows=2,
        cols=2,
        cells={},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(1, 1),
    )


def _trap_grid() -> GridState:
    """3x3 grid with a trap at (0,1)."""
    return GridState(
        rows=3,
        cols=3,
        cells={(0, 1): CellType.TRAP},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(2, 2),
    )


def _make_agent(grid: GridState) -> AgentState:
    return AgentState(
        position=grid.start_pos,
        accumulated_reward=0.0,
        step_count=0,
        is_done=False,
    )


class TestRunStep:
    """Tests for run_step()."""

    def test_run_step_moves_agent(self) -> None:
        grid = _simple_grid()
        qt = init_qtable(grid)
        hp = Hyperparameters(epsilon=1.0, max_steps_per_episode=100)
        new_agent, _ = run_step(
            _make_agent(grid),
            grid,
            qt,
            hp,
            RewardConfig(),
            random.Random(42),
        )
        assert new_agent.step_count == 1

    def test_run_step_accumulates_reward(self) -> None:
        grid = _simple_grid()
        qt = init_qtable(grid)
        hp = Hyperparameters(epsilon=1.0, max_steps_per_episode=100)
        new_agent, _ = run_step(
            _make_agent(grid),
            grid,
            qt,
            hp,
            RewardConfig(),
            random.Random(42),
        )
        assert new_agent.accumulated_reward != 0.0

    def test_run_step_goal_reward_is_exactly_100(self) -> None:
        """Goal reward = +100 clean, no step penalty stacked."""
        grid = GridState(
            rows=2,
            cols=1,
            cells={},
            start_pos=Coordinate(0, 0),
            goal_pos=Coordinate(1, 0),
        )
        qt = init_qtable(grid)
        set_q(qt, 0, 0, Action.DOWN, 100.0)
        hp = Hyperparameters(epsilon=0.0, max_steps_per_episode=100)
        new_agent, _ = run_step(
            _make_agent(grid),
            grid,
            qt,
            hp,
            RewardConfig(),
            random.Random(42),
        )
        assert new_agent.accumulated_reward == 100.0
        assert new_agent.terminal_reason == TerminalReason.GOAL_REACHED

    def test_run_step_trap_terminates_episode(self) -> None:
        grid = _trap_grid()
        qt = init_qtable(grid)
        set_q(qt, 0, 0, Action.RIGHT, 100.0)
        hp = Hyperparameters(epsilon=0.0, max_steps_per_episode=100)
        new_agent, _ = run_step(
            _make_agent(grid),
            grid,
            qt,
            hp,
            RewardConfig(),
            random.Random(42),
        )
        assert new_agent.is_done is True
        assert new_agent.terminal_reason == TerminalReason.TRAP_HIT

    def test_run_step_max_steps_terminates(self) -> None:
        grid = _simple_grid()
        qt = init_qtable(grid)
        hp = Hyperparameters(epsilon=1.0, max_steps_per_episode=1)
        new_agent, _ = run_step(
            _make_agent(grid),
            grid,
            qt,
            hp,
            RewardConfig(),
            random.Random(42),
        )
        assert new_agent.is_done is True


class TestRunEpisode:
    """Tests for run_episode()."""

    def test_run_episode_returns_episode_record(self) -> None:
        grid = _simple_grid()
        qt = init_qtable(grid)
        hp = Hyperparameters(epsilon=1.0, max_steps_per_episode=50)
        _, record = run_episode(grid, qt, hp, RewardConfig(), random.Random(42))
        assert isinstance(record, EpisodeRecord)
        assert record.steps > 0

    def test_run_episode_deterministic_with_same_seed(self) -> None:
        grid = _simple_grid()
        hp = Hyperparameters(epsilon=0.5, max_steps_per_episode=50)
        rewards = RewardConfig()
        _, r1 = run_episode(grid, init_qtable(grid), hp, rewards, random.Random(42))
        _, r2 = run_episode(grid, init_qtable(grid), hp, rewards, random.Random(42))
        assert r1.total_reward == r2.total_reward
        assert r1.steps == r2.steps

    def test_run_step_uses_local_rng(self) -> None:
        """Verify local RNG, not global random."""
        grid = _simple_grid()
        hp = Hyperparameters(epsilon=1.0, max_steps_per_episode=10)
        random.seed(999)
        global_val = random.random()
        random.seed(999)
        run_episode(grid, init_qtable(grid), hp, RewardConfig(), random.Random(42))
        assert random.random() == global_val

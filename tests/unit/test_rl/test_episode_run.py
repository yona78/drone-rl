"""Unit tests for drone_rl.rl.episode module — run_episode execution."""

import random

from drone_rl.rl.episode import run_episode
from drone_rl.rl.qtable import init_qtable
from drone_rl.types.grid import Coordinate, GridState
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

"""Integration tests for edge cases and boundary conditions (PRD §4.3)."""

from __future__ import annotations

import pytest

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.agent import Action, TerminalReason
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import Hyperparameters


def _empty_grid(rows=10, cols=10) -> GridState:
    return GridState(
        rows=rows,
        cols=cols,
        cells={},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(rows - 1, cols - 1),
    )


def test_edge_empty_grid_optimal_path():
    """Test empty grid (no obstacles) — should learn optimal path."""
    sdk = DroneRLSDK(hp=Hyperparameters(total_episodes=200, random_seed=42))
    sdk.create_environment(_empty_grid())
    sdk.train(num_episodes=200)
    path = sdk.play_best_policy(max_steps=50)
    assert len(path) == 19  # Manhattan distance 10x10 is 18 steps, so path length is 19


def test_edge_unreachable_goal():
    """Test unreachable goal (completely surrounded) — should terminate at max steps."""
    grid = _empty_grid()
    grid.cells = {
        (8, 9): CellType.BUILDING,
        (9, 8): CellType.BUILDING,
    }
    hp = Hyperparameters(max_steps_per_episode=20, total_episodes=10, random_seed=42)
    sdk = DroneRLSDK(hp=hp)
    sdk.create_environment(grid)
    records = sdk.train(num_episodes=10)
    assert all(r.terminal_reason == TerminalReason.MAX_STEPS for r in records)


def test_edge_start_equals_goal():
    """Test start position = goal position — should reach goal immediately."""
    grid = _empty_grid()
    grid.start_pos = Coordinate(9, 9)
    sdk = DroneRLSDK(hp=Hyperparameters(total_episodes=5, random_seed=42))
    sdk.create_environment(grid)
    records = sdk.train(num_episodes=5)
    assert all(r.terminal_reason == TerminalReason.GOAL_REACHED for r in records)


def test_edge_grid_boundaries():
    """Test grid boundaries — should not allow out-of-bounds movement."""
    grid = _empty_grid()
    sdk = DroneRLSDK(hp=Hyperparameters(total_episodes=1, max_steps_per_episode=5, random_seed=42))
    sdk.create_environment(grid)
    # Start at 0,0. Move UP should hit boundary.
    state, reward, done = sdk.step(Action.UP)
    assert state.position.row == 0 and state.position.col == 0


def test_edge_zero_learning_rate():
    """Test zero learning rate (α=0) — should raise ValueError."""
    hp = Hyperparameters(alpha=0.0, total_episodes=10, random_seed=42)
    with pytest.raises(ValueError):
        DroneRLSDK(hp=hp)


def test_edge_zero_discount_factor():
    """Test zero discount factor (γ=0) — should maximize immediate reward only."""
    hp = Hyperparameters(gamma=0.0, total_episodes=100, random_seed=42)
    sdk = DroneRLSDK(hp=hp)
    sdk.create_environment(_empty_grid())
    sdk.train(num_episodes=100)
    qt = sdk.get_qtable()
    # It learns something but myopic
    nonzero = sum(1 for action_vals in qt.values() for v in action_vals.values() if v != 0.0)
    assert nonzero > 0


def test_edge_zero_exploration_rate():
    """Test zero exploration rate (ε=0) — should never explore (pure exploitation)."""
    hp = Hyperparameters(
        epsilon=0.0, epsilon_decay=1.0, epsilon_min=0.0, total_episodes=10, random_seed=42
    )
    sdk = DroneRLSDK(hp=hp)
    sdk.create_environment(_empty_grid())
    records = sdk.train(num_episodes=10)
    # Without exploration, it will repeatedly hit max steps or random initial path,
    # but epsilon should remain 0 in records.
    assert all(r.epsilon == 0.0 for r in records)


def test_edge_max_grid_size():
    """Test max grid size (20×20) — should not crash."""
    sdk = DroneRLSDK(hp=Hyperparameters(total_episodes=50, random_seed=42))
    sdk.create_environment(_empty_grid(rows=20, cols=20))
    records = sdk.train(num_episodes=50)
    assert len(records) == 50

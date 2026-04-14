"""Unit tests for DroneRLSDK core — environment, training, control (§4).

Covers create_environment, train, pause, reset, step, and play_best_policy.

Reference: CODE_PLAN Phase 3, §3.4.
"""

from __future__ import annotations

import pytest

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.agent import Action
from drone_rl.types.grid import Coordinate, GridState
from drone_rl.types.rl import Hyperparameters

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tiny_grid() -> GridState:
    """3×3 grid: start (0,0) goal (2,2), no obstacles."""
    return GridState(
        rows=3,
        cols=3,
        cells={},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(2, 2),
    )


@pytest.fixture()
def fast_hp() -> Hyperparameters:
    """Hyperparameters configured for quick 10-episode training."""
    return Hyperparameters(
        alpha=0.5,
        gamma=0.9,
        epsilon=1.0,
        epsilon_decay=0.9,
        epsilon_min=0.01,
        max_steps_per_episode=20,
        total_episodes=10,
        random_seed=42,
    )


@pytest.fixture()
def sdk(tiny_grid: GridState, fast_hp: Hyperparameters) -> DroneRLSDK:
    """SDK with tiny grid already loaded."""
    s = DroneRLSDK(hp=fast_hp)
    s.create_environment(tiny_grid)
    return s


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_sdk_create_environment(tiny_grid: GridState) -> None:
    """create_environment sets grid and initialises a non-empty Q-table."""
    s = DroneRLSDK()
    s.create_environment(tiny_grid)
    qt = s.get_qtable()
    assert isinstance(qt, dict)
    assert len(qt) > 0


def test_sdk_train_returns_training_result(sdk: DroneRLSDK) -> None:
    """train() returns a non-empty list of EpisodeRecord dicts."""
    records = sdk.train(num_episodes=5)
    assert len(records) == 5


def test_sdk_train_updates_qtable(sdk: DroneRLSDK) -> None:
    """Q-table values change after training (not all zero)."""
    qt_before = sdk.get_qtable()
    flat_before = [v for row in qt_before.values() for v in row.values()]
    sdk.train(num_episodes=10)
    qt_after = sdk.get_qtable()
    flat_after = [v for row in qt_after.values() for v in row.values()]
    assert flat_before != flat_after


def test_sdk_pause(sdk: DroneRLSDK) -> None:
    """pause() stops training before all episodes complete."""

    class PauseMiddleware:
        def before_episode_start(self, ep: int) -> None:
            if ep == 2:
                sdk.pause()

        def after_step_update(self, _: object) -> None:
            pass

        def on_episode_complete(self, _: object) -> None:
            pass

        def on_training_pause(self) -> None:
            pass

        def on_training_resume(self) -> None:
            pass

    sdk.register_middleware(PauseMiddleware())
    records = sdk.train(num_episodes=10)
    assert len(records) < 10


def test_sdk_reset(sdk: DroneRLSDK) -> None:
    """reset() clears episode records and resets Q-table."""
    sdk.train(num_episodes=5)
    assert len(sdk.get_episode_stats()) == 5
    sdk.reset()
    assert sdk.get_episode_stats() == []


def test_sdk_step(sdk: DroneRLSDK) -> None:
    """step() returns (AgentState, float reward, bool done). Action is optional."""
    # Test with explicit action
    agent, reward, done = sdk.step(Action.DOWN)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert agent.position.row == 1

    # Test without action (best action)
    sdk.reset()
    agent, reward, done = sdk.step()
    assert isinstance(reward, float)
    assert isinstance(done, bool)

def test_sdk_get_agent_state(sdk: DroneRLSDK) -> None:
    """get_agent_state returns the current agent position."""
    state = sdk.get_agent_state()
    assert state == {"row": 0, "col": 0}

    sdk.step(Action.DOWN)
    state = sdk.get_agent_state()
    assert state == {"row": 1, "col": 0}


def test_sdk_play_best_policy(sdk: DroneRLSDK) -> None:
    """play_best_policy() returns a list of (row, col) tuples."""
    sdk.train(num_episodes=10)
    path = sdk.play_best_policy(max_steps=50)
    assert isinstance(path, list)
    assert len(path) >= 1
    assert all(isinstance(p, tuple) and len(p) == 2 for p in path)

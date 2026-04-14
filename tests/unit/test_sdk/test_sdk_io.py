"""Unit tests for DroneRLSDK I/O and query methods (§4).

Covers save/load policy, save/load layout, export_logs,
get_qtable, and get_episode_stats.

Reference: CODE_PLAN Phase 3, §3.4.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.grid import Coordinate, GridState
from drone_rl.types.rl import Hyperparameters

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tiny_grid() -> GridState:
    """2×2 grid: start (0,0) goal (1,1), no obstacles."""
    return GridState(
        rows=2,
        cols=2,
        cells={},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(1, 1),
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


def test_sdk_save_and_load_policy(sdk: DroneRLSDK) -> None:
    """Saved Q-table round-trips back to an equivalent structure."""
    sdk.train(num_episodes=5)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "policy.json"
        sdk.save_policy(path)
        qt_before = sdk.get_qtable()
        sdk.reset()
        sdk.load_policy(path)
        qt_after = sdk.get_qtable()
    assert qt_before == qt_after


def test_sdk_save_and_load_layout(sdk: DroneRLSDK, tiny_grid: GridState) -> None:
    """Saved layout round-trips: rows/cols/start/goal preserved."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "layout.json"
        sdk.save_layout(path)
        loaded = sdk.load_layout(path)
    assert loaded.rows == tiny_grid.rows
    assert loaded.cols == tiny_grid.cols
    assert loaded.start_pos == tiny_grid.start_pos
    assert loaded.goal_pos == tiny_grid.goal_pos


def test_sdk_load_layout_validation(sdk: DroneRLSDK) -> None:
    """load_layout raises ValueError for invalid file formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "invalid.json"
        # Policy-like format (state keys map to dicts, not ints)
        path.write_text('{"0,0": {"up": 0.0}}')
        with pytest.raises(ValueError, match="Invalid Grid Layout format"):
            sdk.load_layout(path)


def test_sdk_export_logs(sdk: DroneRLSDK) -> None:
    """export_logs writes a CSV with correct column headers."""
    sdk.train(num_episodes=3)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "logs.csv"
        sdk.export_logs(path)
        text = path.read_text()
    assert "episode" in text
    assert "total_reward" in text
    assert "steps" in text


def test_sdk_get_qtable(sdk: DroneRLSDK) -> None:
    """get_qtable() returns a dict with string keys and float values."""
    sdk.train(num_episodes=3)
    qt = sdk.get_qtable()
    for state_key, actions in qt.items():
        assert isinstance(state_key, str)
        for action_key, q_val in actions.items():
            assert isinstance(action_key, str)
            assert isinstance(q_val, float)


def test_sdk_get_episode_stats(sdk: DroneRLSDK) -> None:
    """get_episode_stats() returns list of dicts with required keys."""
    sdk.train(num_episodes=4)
    stats = sdk.get_episode_stats()
    assert len(stats) == 4
    required = {
        "episode",
        "total_reward",
        "steps",
        "terminal_reason",
        "epsilon",
    }
    for stat in stats:
        assert required.issubset(stat.keys())

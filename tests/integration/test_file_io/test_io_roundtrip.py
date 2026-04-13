"""Integration tests for File I/O round-trips (Phase 7).

All I/O goes through DroneRLSDK (§4 boundary). Covers policy JSON,
layout JSON, CSV export, and results JSON (§7.1–§7.4).
"""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import pytest

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import Hyperparameters


@pytest.fixture()
def grid_with_obstacle() -> GridState:
    """4×4 grid with one BUILDING cell; start (0,0) goal (3,3)."""
    return GridState(
        rows=4,
        cols=4,
        cells={(1, 1): CellType.BUILDING},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(3, 3),
    )


@pytest.fixture()
def trained_sdk(grid_with_obstacle: GridState) -> DroneRLSDK:
    """SDK trained for 20 fast episodes."""
    hp = Hyperparameters(
        alpha=0.5,
        gamma=0.9,
        epsilon=1.0,
        epsilon_decay=0.9,
        epsilon_min=0.01,
        max_steps_per_episode=30,
        total_episodes=20,
        random_seed=7,
    )
    sdk = DroneRLSDK(hp=hp)
    sdk.create_environment(grid_with_obstacle)
    sdk.train(num_episodes=20)
    return sdk


# --- §7.1 Policy JSON ---


def test_policy_json_is_human_readable(trained_sdk: DroneRLSDK) -> None:
    """Saved policy file is valid JSON with string keys."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "policy.json"
        trained_sdk.save_policy(p)
        data = json.loads(p.read_text())
    assert isinstance(data, dict)
    for state_key, actions in data.items():
        assert isinstance(state_key, str)
        assert isinstance(actions, dict)


def test_policy_round_trip_preserves_values(trained_sdk: DroneRLSDK) -> None:
    """Q-table values survive save → load → compare."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "policy.json"
        trained_sdk.save_policy(p)
        qt_before = trained_sdk.get_qtable()
        trained_sdk.reset()
        trained_sdk.load_policy(p)
        qt_after = trained_sdk.get_qtable()
    assert qt_before == qt_after


# --- §7.2 Layout JSON ---


def test_layout_json_has_required_fields(
    trained_sdk: DroneRLSDK, grid_with_obstacle: GridState
) -> None:
    """Layout JSON includes rows, cols, cells, start_pos, goal_pos."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "layout.json"
        trained_sdk.save_layout(p)
        data = json.loads(p.read_text())
    assert data["rows"] == grid_with_obstacle.rows
    assert data["cols"] == grid_with_obstacle.cols
    assert "cells" in data
    assert "start_pos" in data
    assert "goal_pos" in data


def test_layout_round_trip_preserves_obstacle(trained_sdk: DroneRLSDK) -> None:
    """BUILDING cell at (1,1) survives save → load."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "layout.json"
        trained_sdk.save_layout(p)
        loaded = trained_sdk.load_layout(p)
    assert loaded.cells.get((1, 1)) == CellType.BUILDING


# --- §7.3 CSV export ---


def test_csv_export_has_all_columns(trained_sdk: DroneRLSDK) -> None:
    """CSV contains all expected header columns."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "log.csv"
        trained_sdk.export_logs(p)
        with p.open() as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames or []
    required = {
        "episode",
        "total_reward",
        "steps",
        "terminal_reason",
        "epsilon_used",
        "success_rate",
    }
    assert required.issubset(set(headers))


def test_csv_row_count_matches_episodes(trained_sdk: DroneRLSDK) -> None:
    """CSV has exactly as many data rows as trained episodes."""
    stats = trained_sdk.get_episode_stats()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "log.csv"
        trained_sdk.export_logs(p)
        with p.open() as fh:
            rows = list(csv.DictReader(fh))
    assert len(rows) == len(stats)


# --- §7.4 Results storage ---


def test_results_json_has_summary_keys(trained_sdk: DroneRLSDK) -> None:
    """Results JSON contains total_episodes, success_rate, mean_reward."""
    meta = {"experiment": "phase7-test", "seed": 7}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "results.json"
        trained_sdk.save_results(p, metadata=meta)
        data = json.loads(p.read_text())
    assert data["total_episodes"] == 20
    assert "success_rate" in data
    assert "mean_reward" in data
    assert "mean_steps" in data
    assert data["metadata"]["experiment"] == "phase7-test"


def test_results_success_rate_in_range(trained_sdk: DroneRLSDK) -> None:
    """success_rate is a float in [0.0, 1.0]."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "results.json"
        trained_sdk.save_results(p)
        data = json.loads(p.read_text())
    sr = data["success_rate"]
    assert isinstance(sr, float)
    assert 0.0 <= sr <= 1.0

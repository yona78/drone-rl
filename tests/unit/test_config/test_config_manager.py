"""Unit tests for ConfigManager (§6.3 graceful degradation — Dr. Segal).

Covers loading each config file, validation, missing-file fallback,
and corrupted-JSON fallback.

Reference: CODE_PLAN Phase 3, §3.5 / §6.3.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from drone_rl.shared.config import ConfigManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_valid_configs(cfg_dir: Path) -> None:
    """Write all three valid config files into cfg_dir."""
    (cfg_dir / "setup.json").write_text(
        json.dumps({"version": "1.00", "grid": {}, "ui": {}})
    )
    (cfg_dir / "rewards.json").write_text(
        json.dumps({
            "version": "1.00",
            "goal_reached": 100.0,
            "empty_step": -1.0,
            "building_collision": -10.0,
            "trap_hit": -100.0,
            "crosswind_penalty": -10.0,
        })
    )
    (cfg_dir / "hyperparameters.json").write_text(
        json.dumps({
            "version": "1.00",
            "alpha": 0.1,
            "gamma": 0.99,
            "epsilon": 1.0,
            "epsilon_decay": 0.995,
            "epsilon_min": 0.01,
            "max_steps_per_episode": 500,
            "total_episodes": 1000,
            "random_seed": 42,
        })
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_config_manager_load_setup() -> None:
    """load_setup() returns dict with 'version' key from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        cm = ConfigManager(cfg_dir)
        data = cm.load_setup()
    assert "version" in data
    assert data["version"] == "1.00"


def test_config_manager_load_rewards() -> None:
    """load_rewards() returns a dict containing 'goal_reached'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        cm = ConfigManager(cfg_dir)
        data = cm.load_rewards()
    assert "goal_reached" in data
    assert data["goal_reached"] == 100.0


def test_config_manager_load_hyperparameters() -> None:
    """load_hyperparameters() returns dict with 'alpha' key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        cm = ConfigManager(cfg_dir)
        data = cm.load_hyperparameters()
    assert "alpha" in data
    assert data["alpha"] == 0.1


def test_config_manager_validate_config_success() -> None:
    """validate_config() returns True when all three files are present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        cm = ConfigManager(cfg_dir)
        assert cm.validate_config() is True


def test_config_manager_validate_config_missing_file() -> None:
    """validate_config() returns False when a config file is absent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        (cfg_dir / "rewards.json").unlink()
        cm = ConfigManager(cfg_dir)
        assert cm.validate_config() is False


def test_config_manager_validate_config_invalid_json() -> None:
    """validate_config() returns False when a file contains invalid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        (cfg_dir / "setup.json").write_text("{bad json}")
        cm = ConfigManager(cfg_dir)
        assert cm.validate_config() is False


def test_config_manager_version_check() -> None:
    """Version field in each loaded config is a non-empty string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir)
        _write_valid_configs(cfg_dir)
        cm = ConfigManager(cfg_dir)
        for loader in (cm.load_setup, cm.load_rewards, cm.load_hyperparameters):
            data = loader()
            assert "version" in data
            assert isinstance(data["version"], str)
            assert len(data["version"]) > 0

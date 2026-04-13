"""
Configuration Manager for the 2D Drone Pathfinding RL simulation.

Loads JSON config files from the config/ directory with graceful
degradation: if a file is missing or corrupted, logs a warning and
falls back to constants.py defaults (Fix 11: §6.3 & §20.4 — MANDATORY).

Reference: CODE_PLAN section 3.5, Dr. Segal §7.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..constants import (
    ALPHA_DEFAULT,
    EPSILON_DECAY_DEFAULT,
    EPSILON_DEFAULT,
    EPSILON_MIN_DEFAULT,
    GAMMA_DEFAULT,
    GRID_HEIGHT_DEFAULT,
    GRID_HEIGHT_MAX,
    GRID_WIDTH_DEFAULT,
    GRID_WIDTH_MAX,
    MAX_STEPS_DEFAULT,
    RANDOM_SEED_DEFAULT,
    REWARD_BUILDING_COLLISION,
    REWARD_CROSSWIND,
    REWARD_GOAL,
    REWARD_STEP,
    REWARD_TRAP_HIT,
    TOTAL_EPISODES_DEFAULT,
)

log = logging.getLogger(__name__)

_SETUP_DEFAULTS: dict = {
    "version": "1.00",
    "grid": {
        "default_width": GRID_WIDTH_DEFAULT,
        "default_height": GRID_HEIGHT_DEFAULT,
        "max_width": GRID_WIDTH_MAX,
        "max_height": GRID_HEIGHT_MAX,
    },
    "ui": {"window_width": 1400, "window_height": 900},
}

_REWARDS_DEFAULTS: dict = {
    "version": "1.00",
    "goal_reached": REWARD_GOAL,
    "empty_step": REWARD_STEP,
    "building_collision": REWARD_BUILDING_COLLISION,
    "trap_hit": REWARD_TRAP_HIT,
    "crosswind_penalty": REWARD_CROSSWIND,
}

_HP_DEFAULTS: dict = {
    "version": "1.00",
    "alpha": ALPHA_DEFAULT,
    "gamma": GAMMA_DEFAULT,
    "epsilon": EPSILON_DEFAULT,
    "epsilon_decay": EPSILON_DECAY_DEFAULT,
    "epsilon_min": EPSILON_MIN_DEFAULT,
    "max_steps_per_episode": MAX_STEPS_DEFAULT,
    "total_episodes": TOTAL_EPISODES_DEFAULT,
    "random_seed": RANDOM_SEED_DEFAULT,
}


def _load_json(path: Path, defaults: dict) -> dict:
    """Load JSON with graceful degradation on missing or corrupted file."""
    try:
        with path.open() as fh:
            return json.load(fh)
    except FileNotFoundError:
        log.warning("Config file not found: %s — using defaults", path)
        return dict(defaults)
    except json.JSONDecodeError as exc:
        log.warning("Corrupted JSON in %s (%s) — using defaults", path, exc)
        return dict(defaults)


class ConfigManager:
    """
    Loads and validates JSON configuration files.

    Falls back to constants.py defaults on missing or corrupted files
    (graceful degradation — Fix 11: §6.3).

    Input Data: path to config/ directory.
    Output Data: validated dicts from load_setup/rewards/hyperparameters.
    Setup Data: config_dir resolved at init.
    """

    def __init__(self, config_dir: Path) -> None:
        self._dir = Path(config_dir)

    def load_setup(self) -> dict:
        """Load config/setup.json; fall back to defaults on error."""
        return _load_json(self._dir / "setup.json", _SETUP_DEFAULTS)

    def load_rewards(self) -> dict:
        """Load config/rewards.json; fall back to defaults on error."""
        return _load_json(self._dir / "rewards.json", _REWARDS_DEFAULTS)

    def load_hyperparameters(self) -> dict:
        """Load config/hyperparameters.json; fall back to defaults on error."""
        return _load_json(self._dir / "hyperparameters.json", _HP_DEFAULTS)

    def validate_config(self) -> bool:
        """Return True if all three config files exist and parse as JSON."""
        for name in ("setup.json", "rewards.json", "hyperparameters.json"):
            p = self._dir / name
            if not p.exists():
                return False
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError:
                return False
        return True

"""
File I/O helpers for the DroneRLSDK.

Pure functions for serializing and deserializing Q-tables, grid layouts,
and episode CSV logs. All paths must be absolute (use pathlib).

Reference: CODE_PLAN section 14, Phase 3.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from ..rl.qtable import qtable_from_dict, qtable_to_dict
from ..types.agent import Action
from ..types.grid import CellType, Coordinate, GridState
from ..types.rl import EpisodeRecord, QTable

# --- Policy (Q-table) ---

def save_policy(qtable: QTable, filepath: Path) -> None:
    """Serialize Q-table to JSON at filepath."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(qtable_to_dict(qtable), indent=2))


def load_policy(filepath: Path) -> QTable:
    """Deserialize Q-table from JSON file."""
    return qtable_from_dict(json.loads(Path(filepath).read_text()))


# --- Layout (GridState) ---

def _grid_to_dict(grid: GridState) -> dict:
    """Convert GridState to JSON-serializable dict."""
    return {
        "rows": grid.rows,
        "cols": grid.cols,
        "cells": {
            f"{r},{c}": ct.value for (r, c), ct in grid.cells.items()
        },
        "start_pos": [grid.start_pos.row, grid.start_pos.col],
        "goal_pos": [grid.goal_pos.row, grid.goal_pos.col],
        "wind_directions": {
            f"{r},{c}": a.value
            for (r, c), a in grid.wind_directions.items()
        },
    }


def _grid_from_dict(data: dict) -> GridState:
    """Reconstruct GridState from dict."""
    ct_map = {ct.value: ct for ct in CellType}
    a_map = {a.value: a for a in Action}
    cells = {
        tuple(int(x) for x in k.split(",")): ct_map[v]  # type: ignore[misc]
        for k, v in data.get("cells", {}).items()
    }
    wind = {
        tuple(int(x) for x in k.split(",")): a_map[v]  # type: ignore[misc]
        for k, v in data.get("wind_directions", {}).items()
    }
    return GridState(
        rows=data["rows"],
        cols=data["cols"],
        cells=cells,  # type: ignore[arg-type]
        start_pos=Coordinate(*data["start_pos"]),
        goal_pos=Coordinate(*data["goal_pos"]),
        wind_directions=wind,  # type: ignore[arg-type]
    )


def save_layout(grid: GridState, filepath: Path) -> None:
    """Serialize GridState to JSON at filepath."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(_grid_to_dict(grid), indent=2))


def load_layout(filepath: Path) -> GridState:
    """Deserialize GridState from JSON file."""
    return _grid_from_dict(json.loads(Path(filepath).read_text()))


# --- Episode Logs ---

def export_logs(records: list[EpisodeRecord], filepath: Path) -> None:
    """Export episode records as CSV."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["episode", "total_reward", "steps",
                        "terminal_reason", "epsilon"],
        )
        writer.writeheader()
        for r in records:
            writer.writerow({
                "episode": r.episode,
                "total_reward": r.total_reward,
                "steps": r.steps,
                "terminal_reason": r.terminal_reason.value,
                "epsilon": r.epsilon,
            })

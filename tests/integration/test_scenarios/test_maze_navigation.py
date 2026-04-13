"""Acceptance test: maze navigation on a 10x10 grid with building walls.

The agent must navigate a U-shaped corridor of BUILDING obstacles to reach
the goal. Success criterion: >= 70% goal-reach rate in the final 100 episodes
after 1000 training episodes.

Layout (B=Building, S=Start, G=Goal, .=Empty):

  S . . . . . . . . .
  . B B B B B B B . .
  . B . . . . . B . .
  . B . . . . . B . .
  . B . . . . . B . .
  . B . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . G
"""

from __future__ import annotations

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.agent import TerminalReason
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import EpisodeRecord, Hyperparameters

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _maze_grid() -> GridState:
    """10x10 grid with a U-shaped building corridor."""
    buildings = (
        # top wall of U (row 1, cols 1-7)
        [(1, c) for c in range(1, 8)]
        # left wall of U (rows 2-4, col 1)
        + [(r, 1) for r in range(2, 5)]
        # right wall of U (rows 2-4, col 7)
        + [(r, 7) for r in range(2, 5)]
    )
    cells: dict[tuple[int, int], CellType] = dict.fromkeys(buildings, CellType.BUILDING)
    return GridState(
        rows=10,
        cols=10,
        cells=cells,
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(9, 9),
    )


def _maze_hp(seed: int = 0) -> Hyperparameters:
    return Hyperparameters(
        alpha=0.1,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.993,
        epsilon_min=0.05,
        max_steps_per_episode=500,
        total_episodes=1000,
        random_seed=seed,
    )


def _success_rate(records: list[EpisodeRecord], last_n: int = 100) -> float:
    tail = records[-last_n:]
    if not tail:
        return 0.0
    return sum(1 for r in tail if r.terminal_reason == TerminalReason.GOAL_REACHED) / len(tail)


# ---------------------------------------------------------------------------
# Scenario tests
# ---------------------------------------------------------------------------


def test_maze_navigation_success_rate_ge_70pct() -> None:
    """Agent reaches goal >= 70% of the time in final 100 of 1000 episodes."""
    sdk = DroneRLSDK(hp=_maze_hp(seed=42))
    sdk.create_environment(_maze_grid())
    records = sdk.train(num_episodes=1000)

    rate = _success_rate(records, last_n=100)
    assert rate >= 0.70, f"Expected >= 70% success rate in maze, got {rate:.1%}"


def test_maze_buildings_are_not_goal_cells() -> None:
    """Sanity: none of the building cells coincide with start or goal."""
    grid = _maze_grid()
    assert grid.cells.get((0, 0)) is None, "Start cell must not be BUILDING"
    assert grid.cells.get((9, 9)) is None, "Goal cell must not be BUILDING"


def test_maze_episode_count_matches_requested() -> None:
    """train(num_episodes=300) returns exactly 300 records."""
    sdk = DroneRLSDK(hp=_maze_hp(seed=5))
    sdk.create_environment(_maze_grid())
    records = sdk.train(num_episodes=300)
    assert len(records) == 300


def test_maze_training_produces_nonzero_qtable() -> None:
    """Q-table is non-trivially populated after maze training."""
    sdk = DroneRLSDK(hp=_maze_hp(seed=13))
    sdk.create_environment(_maze_grid())
    sdk.train(num_episodes=200)

    qt = sdk.get_qtable()
    nonzero = sum(1 for action_vals in qt.values() for v in action_vals.values() if v != 0.0)
    assert nonzero > 0, "Q-table still all zeros after 200 episodes"


def test_maze_reset_clears_records() -> None:
    """reset() after maze training clears episode history."""
    sdk = DroneRLSDK(hp=_maze_hp(seed=3))
    sdk.create_environment(_maze_grid())
    sdk.train(num_episodes=50)
    assert len(sdk.get_episode_stats()) == 50
    sdk.reset()
    assert sdk.get_episode_stats() == []

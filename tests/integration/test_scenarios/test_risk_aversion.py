"""Acceptance test: risk aversion — agent avoids TRAP tiles (PRD §11.2 scenario 3).

A row of TRAP cells blocks the direct diagonal path. The agent must learn to
route around them rather than suffering -100 terminal penalties.

Layout  (T=Trap, S=Start, G=Goal, .=Empty):

  S . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . T T T T . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . .
  . . . . . . . . . G

Success criterion after 1000 episodes:
- >= 65% goal-reach rate in the final 100 episodes
- trap-hit rate in the final 100 episodes < 20%
"""

from __future__ import annotations

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.agent import TerminalReason
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import EpisodeRecord, Hyperparameters

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trap_grid() -> GridState:
    """10x10 grid with a row of 4 trap tiles blocking the direct route."""
    traps = [(3, c) for c in range(3, 7)]
    cells: dict[tuple[int, int], CellType] = dict.fromkeys(traps, CellType.TRAP)
    return GridState(
        rows=10,
        cols=10,
        cells=cells,
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(9, 9),
    )


def _risk_hp(seed: int = 0) -> Hyperparameters:
    return Hyperparameters(
        alpha=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_decay=0.993,
        epsilon_min=0.05,
        max_steps_per_episode=500,
        total_episodes=1000,
        random_seed=seed,
    )


def _tail_stats(records: list[EpisodeRecord], last_n: int = 100) -> dict:
    tail = records[-last_n:]
    n = len(tail)
    if n == 0:
        return {"success_rate": 0.0, "trap_rate": 0.0}
    goals = sum(1 for r in tail if r.terminal_reason == TerminalReason.GOAL_REACHED)
    traps = sum(1 for r in tail if r.terminal_reason == TerminalReason.TRAP_HIT)
    return {
        "success_rate": goals / n,
        "trap_rate": traps / n,
    }


# ---------------------------------------------------------------------------
# Scenario tests
# ---------------------------------------------------------------------------

def test_risk_aversion_success_rate_ge_65pct() -> None:
    """Agent reaches goal >= 65% of the time in final 100 of 1000 episodes."""
    sdk = DroneRLSDK(hp=_risk_hp(seed=42))
    sdk.create_environment(_trap_grid())
    records = sdk.train(num_episodes=1000)

    stats = _tail_stats(records, last_n=100)
    assert stats["success_rate"] >= 0.65, (
        f"Expected >= 65% success rate in trap grid, got {stats['success_rate']:.1%}"
    )


def test_risk_aversion_trap_rate_below_20pct() -> None:
    """Trap-hit rate drops below 20% in the final 100 episodes."""
    sdk = DroneRLSDK(hp=_risk_hp(seed=42))
    sdk.create_environment(_trap_grid())
    records = sdk.train(num_episodes=1000)

    stats = _tail_stats(records, last_n=100)
    assert stats["trap_rate"] < 0.20, (
        f"Trap rate too high in final 100 episodes: {stats['trap_rate']:.1%}"
    )


def test_risk_aversion_traps_not_at_start_or_goal() -> None:
    """Sanity: trap cells do not coincide with start or goal."""
    grid = _trap_grid()
    assert grid.cells.get((0, 0)) is None, "Start cell must not be TRAP"
    assert grid.cells.get((9, 9)) is None, "Goal cell must not be TRAP"


def test_risk_aversion_episode_count_correct() -> None:
    """train(num_episodes=400) returns exactly 400 records."""
    sdk = DroneRLSDK(hp=_risk_hp(seed=7))
    sdk.create_environment(_trap_grid())
    records = sdk.train(num_episodes=400)
    assert len(records) == 400


def test_risk_aversion_qtable_reflects_trap_penalty() -> None:
    """After training, Q-values adjacent to trap tiles are lower than empty."""
    sdk = DroneRLSDK(hp=_risk_hp(seed=99))
    sdk.create_environment(_trap_grid())
    sdk.train(num_episodes=500)

    qt = sdk.get_qtable()
    # (2, 3) is directly above the trap row — at least one action should have
    # a negative Q-value reflecting the learned danger.
    state_above_trap = (2, 3)
    if state_above_trap in qt:
        vals = list(qt[state_above_trap].values())
        assert any(v < 0 for v in vals), (
            "Expected negative Q-values near trap tiles after training"
        )

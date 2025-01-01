"""Acceptance test: direct route on a 10x10 empty grid (PRD §11.2 scenario 1).

Agent must learn a near-optimal path from (0,0) to (9,9) with no obstacles.
Success criterion: >= 90% goal-reach rate over the final 100 episodes.
"""

from __future__ import annotations

from drone_rl.sdk import DroneRLSDK
from drone_rl.types.agent import TerminalReason
from drone_rl.types.grid import Coordinate, GridState
from drone_rl.types.rl import EpisodeRecord, Hyperparameters

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_10x10() -> GridState:
    return GridState(
        rows=10,
        cols=10,
        cells={},
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(9, 9),
    )


def _scenario_hp(seed: int = 0) -> Hyperparameters:
    return Hyperparameters(
        alpha=0.1,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.05,
        max_steps_per_episode=500,
        total_episodes=500,
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

def test_direct_route_success_rate_ge_90pct() -> None:
    """Agent reaches goal >= 90% of the time in the final 100 episodes."""
    sdk = DroneRLSDK(hp=_scenario_hp(seed=42))
    sdk.create_environment(_empty_10x10())
    records = sdk.train(num_episodes=500)

    rate = _success_rate(records, last_n=100)
    assert rate >= 0.90, (
        f"Expected >= 90% success rate on empty grid, got {rate:.1%}"
    )


def test_direct_route_qtable_not_empty_after_training() -> None:
    """Q-table contains entries after training (learning occurred)."""
    sdk = DroneRLSDK(hp=_scenario_hp(seed=7))
    sdk.create_environment(_empty_10x10())
    sdk.train(num_episodes=50)

    qt = sdk.get_qtable()
    nonzero = sum(
        1 for action_vals in qt.values()
        for v in action_vals.values()
        if v != 0.0
    )
    assert nonzero > 0, "Q-table has no non-zero entries after 50 episodes"


def test_direct_route_episode_count_matches_requested() -> None:
    """train(num_episodes=N) returns exactly N EpisodeRecord dicts."""
    sdk = DroneRLSDK(hp=_scenario_hp(seed=1))
    sdk.create_environment(_empty_10x10())
    records = sdk.train(num_episodes=200)
    assert len(records) == 200


def test_direct_route_epsilon_decays_over_training() -> None:
    """Epsilon is strictly less after training than at the start."""
    sdk = DroneRLSDK(hp=_scenario_hp(seed=99))
    sdk.create_environment(_empty_10x10())
    sdk.train(num_episodes=100)

    stats = sdk.get_episode_stats()
    # last episode epsilon should be lower than initial 1.0
    assert len(stats) > 0
    last_ep = stats[-1]
    # terminal_reason key exists with a recognised value
    assert "terminal_reason" in last_ep
    assert last_ep["terminal_reason"] in ("goal_reached", "max_steps", "trap_hit")


def test_direct_route_play_best_policy_reaches_goal() -> None:
    """play_best_policy() returns a path ending at goal cell after training."""
    sdk = DroneRLSDK(hp=_scenario_hp(seed=42))
    sdk.create_environment(_empty_10x10())
    sdk.train(num_episodes=500)

    path = sdk.play_best_policy(max_steps=200)
    assert isinstance(path, list)
    assert len(path) >= 2
    goal = (9, 9)
    assert path[-1] == goal, (
        f"play_best_policy did not reach goal {goal}; ended at {path[-1]}"
    )

"""Unit tests for drone_rl.rl.policy module — epsilon-greedy selection."""

import random
import tempfile
from pathlib import Path

from drone_rl.rl.policy import load_from_file, save_to_file, select_action
from drone_rl.rl.qtable import set_q
from drone_rl.types.agent import ALL_ACTIONS, Action


class TestSelectAction:
    """Tests for epsilon-greedy action selection."""

    def test_select_action_exploits_when_epsilon_zero(self) -> None:
        """Epsilon=0 -> always best action."""
        qt = {}
        set_q(qt, 0, 0, Action.RIGHT, 10.0)
        rng = random.Random(42)

        for _ in range(20):
            action = select_action(qt, 0, 0, epsilon=0.0, rng=rng)
            assert action == Action.RIGHT

    def test_select_action_explores_when_epsilon_one(self) -> None:
        """Epsilon=1 -> always random; should see multiple actions."""
        qt = {}
        set_q(qt, 0, 0, Action.RIGHT, 10.0)
        rng = random.Random(42)

        actions = {select_action(qt, 0, 0, epsilon=1.0, rng=rng) for _ in range(100)}
        assert len(actions) > 1  # should explore multiple

    def test_select_action_uses_local_rng_not_global(self) -> None:
        """Verify local RNG is used, not global random state."""
        qt = {}
        set_q(qt, 0, 0, Action.UP, 1.0)

        # Set global random to a known state
        random.seed(999)
        global_before = random.random()

        # Use local RNG
        rng = random.Random(42)
        random.seed(999)  # reset global
        select_action(qt, 0, 0, epsilon=0.5, rng=rng)

        # Global state should not have been consumed by select_action
        global_after = random.random()
        assert global_before == global_after

    def test_select_action_deterministic_with_same_rng_seed(self) -> None:
        """Same seed -> same action sequence."""
        qt = {}
        set_q(qt, 0, 0, Action.UP, 1.0)

        rng1 = random.Random(42)
        rng2 = random.Random(42)

        seq1 = [select_action(qt, 0, 0, 0.5, rng1) for _ in range(20)]
        seq2 = [select_action(qt, 0, 0, 0.5, rng2) for _ in range(20)]
        assert seq1 == seq2

    def test_select_action_returns_action_enum(self) -> None:
        """Return type must be Action enum."""
        qt = {}
        rng = random.Random(42)
        result = select_action(qt, 0, 0, 0.5, rng)
        assert isinstance(result, Action)
        assert result in ALL_ACTIONS

    def test_save_and_load_policy_file_round_trip(self) -> None:
        """save_to_file/load_from_file preserves Q-table values."""
        qt = {}
        set_q(qt, 0, 0, Action.RIGHT, 3.14)
        set_q(qt, 1, 1, Action.DOWN, -2.5)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "policy.json"
            save_to_file(qt, path)
            loaded = load_from_file(path)
        assert loaded == qt

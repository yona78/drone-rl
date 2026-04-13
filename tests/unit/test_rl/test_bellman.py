"""Unit tests for drone_rl.rl.bellman module — hand-traced Bellman updates."""

from drone_rl.rl.bellman import bellman_update
from drone_rl.rl.qtable import get_q, set_q
from drone_rl.types.agent import Action
from drone_rl.types.rl import Hyperparameters


class TestBellmanUpdate:
    """Hand-traced Bellman update verification."""

    def test_bellman_update_hand_traced(self) -> None:
        """
        Hand trace:
        Q(s,a) = 0.0, R = -1.0, max Q(s',a') = 5.0
        alpha=0.1, gamma=0.99
        td_target = -1.0 + 0.99 * 5.0 = 3.95
        td_error  = 3.95 - 0.0 = 3.95
        new_q     = 0.0 + 0.1 * 3.95 = 0.395
        """
        qt = {}
        set_q(qt, 1, 1, Action.RIGHT, 5.0)  # next state has value
        hp = Hyperparameters(alpha=0.1, gamma=0.99)

        qt = bellman_update(
            qt,
            row=0,
            col=0,
            action=Action.UP,
            reward=-1.0,
            next_row=1,
            next_col=1,
            is_done=False,
            hp=hp,
        )
        result = get_q(qt, 0, 0, Action.UP)
        assert abs(result - 0.395) < 1e-6

    def test_bellman_update_learning_rate_effect(self) -> None:
        """Higher alpha -> bigger update."""
        qt_lo = {}
        qt_hi = {}
        hp_lo = Hyperparameters(alpha=0.1, gamma=0.99)
        hp_hi = Hyperparameters(alpha=0.5, gamma=0.99)

        qt_lo = bellman_update(
            qt_lo,
            0,
            0,
            Action.UP,
            10.0,
            0,
            1,
            False,
            hp_lo,
        )
        qt_hi = bellman_update(
            qt_hi,
            0,
            0,
            Action.UP,
            10.0,
            0,
            1,
            False,
            hp_hi,
        )
        assert get_q(qt_hi, 0, 0, Action.UP) > get_q(qt_lo, 0, 0, Action.UP)

    def test_bellman_update_discount_factor_effect(self) -> None:
        """Higher gamma -> future matters more."""
        qt_lo = {}
        qt_hi = {}
        set_q(qt_lo, 0, 1, Action.UP, 10.0)
        set_q(qt_hi, 0, 1, Action.UP, 10.0)

        hp_lo = Hyperparameters(alpha=0.1, gamma=0.5)
        hp_hi = Hyperparameters(alpha=0.1, gamma=0.99)

        qt_lo = bellman_update(
            qt_lo,
            0,
            0,
            Action.RIGHT,
            -1.0,
            0,
            1,
            False,
            hp_lo,
        )
        qt_hi = bellman_update(
            qt_hi,
            0,
            0,
            Action.RIGHT,
            -1.0,
            0,
            1,
            False,
            hp_hi,
        )
        assert get_q(qt_hi, 0, 0, Action.RIGHT) > get_q(
            qt_lo,
            0,
            0,
            Action.RIGHT,
        )

    def test_bellman_update_zero_learning_rate(self) -> None:
        """Alpha=0 -> Q-value unchanged."""
        qt = {}
        set_q(qt, 0, 0, Action.UP, 3.0)
        hp = Hyperparameters(alpha=0.0, gamma=0.99)

        qt = bellman_update(qt, 0, 0, Action.UP, 10.0, 0, 1, False, hp)
        assert get_q(qt, 0, 0, Action.UP) == 3.0

    def test_bellman_update_zero_discount_factor(self) -> None:
        """Gamma=0 -> future Q-value ignored."""
        qt = {}
        set_q(qt, 0, 1, Action.UP, 100.0)  # big future value
        hp = Hyperparameters(alpha=1.0, gamma=0.0)

        qt = bellman_update(qt, 0, 0, Action.RIGHT, -1.0, 0, 1, False, hp)
        # new_q = 0 + 1.0 * (-1.0 + 0 * 100 - 0) = -1.0
        assert abs(get_q(qt, 0, 0, Action.RIGHT) - (-1.0)) < 1e-6

    def test_bellman_update_terminal_state(self) -> None:
        """Terminal state -> future Q = 0."""
        qt = {}
        set_q(qt, 0, 1, Action.UP, 100.0)
        hp = Hyperparameters(alpha=1.0, gamma=0.99)

        qt = bellman_update(
            qt,
            0,
            0,
            Action.RIGHT,
            100.0,
            0,
            1,
            True,
            hp,
        )
        # is_done=True -> future_q=0 -> new_q = 0 + 1.0*(100 + 0 - 0) = 100
        assert abs(get_q(qt, 0, 0, Action.RIGHT) - 100.0) < 1e-6

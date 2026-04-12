"""Unit tests for drone_rl.types.rl module."""

from drone_rl.types.agent import Action, TerminalReason
from drone_rl.types.rl import (
    EpisodeRecord,
    Hyperparameters,
    RewardConfig,
    state_key,
)


class TestStateKey:
    """Tests for state_key() builder."""

    def test_state_key_format(self) -> None:
        assert state_key(3, 5) == "3,5"

    def test_state_key_zero(self) -> None:
        assert state_key(0, 0) == "0,0"

    def test_state_key_large(self) -> None:
        assert state_key(19, 19) == "19,19"


class TestQTable:
    """Tests for QTable type alias."""

    def test_qtable_uses_action_enum_keys(self) -> None:
        qt: dict[str, dict[Action, float]] = {
            "0,0": {
                Action.UP: 0.0,
                Action.DOWN: 1.5,
                Action.LEFT: -0.5,
                Action.RIGHT: 2.0,
            },
        }
        assert Action.UP in qt["0,0"]
        assert Action.RIGHT in qt["0,0"]
        # Keys must be Action enum, not strings
        assert "up" not in qt["0,0"]  # type: ignore[operator]


class TestHyperparameters:
    """Tests for Hyperparameters dataclass."""

    def test_hyperparameters_defaults(self) -> None:
        hp = Hyperparameters()
        assert hp.alpha == 0.1
        assert hp.gamma == 0.99
        assert hp.epsilon == 1.0
        assert hp.epsilon_decay == 0.995
        assert hp.epsilon_min == 0.01
        assert hp.max_steps_per_episode == 500
        assert hp.total_episodes == 1000
        assert hp.random_seed == 42


class TestRewardConfig:
    """Tests for RewardConfig dataclass."""

    def test_reward_config_exact_values(self) -> None:
        rc = RewardConfig()
        assert rc.goal_reached == 100.0
        assert rc.empty_step == -1.0
        assert rc.building_collision == -10.0
        assert rc.trap_hit == -100.0
        assert rc.crosswind_penalty == -10.0

    def test_reward_config_custom_values(self) -> None:
        rc = RewardConfig(goal_reached=200.0, trap_hit=-50.0)
        assert rc.goal_reached == 200.0
        assert rc.trap_hit == -50.0


class TestEpisodeRecord:
    """Tests for EpisodeRecord dataclass."""

    def test_episode_record_creation(self) -> None:
        record = EpisodeRecord(
            episode=0,
            total_reward=85.0,
            steps=15,
            terminal_reason=TerminalReason.GOAL_REACHED,
            epsilon=0.95,
        )
        assert record.episode == 0
        assert record.total_reward == 85.0
        assert record.steps == 15
        assert record.terminal_reason == TerminalReason.GOAL_REACHED
        assert record.epsilon == 0.95

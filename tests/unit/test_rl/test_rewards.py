"""Unit tests for drone_rl.rl.rewards module — PRD section 4.1 exact values."""

from drone_rl.rl.rewards import compute_reward
from drone_rl.types.grid import CellType
from drone_rl.types.rl import RewardConfig


class TestComputeReward:
    """Verify every reward value matches PRD section 4.1 defaults."""

    def setup_method(self) -> None:
        self.config = RewardConfig()

    def test_reward_goal_is_plus_100(self) -> None:
        assert compute_reward(CellType.GOAL, self.config) == 100.0

    def test_reward_step_is_minus_1(self) -> None:
        assert compute_reward(CellType.EMPTY, self.config) == -1.0

    def test_reward_start_is_minus_1(self) -> None:
        """Start tile treated as normal step."""
        assert compute_reward(CellType.START, self.config) == -1.0

    def test_reward_building_is_minus_10(self) -> None:
        assert compute_reward(CellType.BUILDING, self.config) == -10.0

    def test_reward_trap_is_minus_100(self) -> None:
        assert compute_reward(CellType.TRAP, self.config) == -100.0

    def test_reward_crosswind_is_minus_10(self) -> None:
        assert compute_reward(CellType.CROSSWIND, self.config) == -10.0

    def test_all_celltypes_covered(self) -> None:
        """Every CellType should return a non-zero reward (or valid 0)."""
        for ct in CellType:
            result = compute_reward(ct, self.config)
            assert isinstance(result, float)

    def test_custom_reward_config(self) -> None:
        custom = RewardConfig(goal_reached=200.0, trap_hit=-50.0)
        assert compute_reward(CellType.GOAL, custom) == 200.0
        assert compute_reward(CellType.TRAP, custom) == -50.0

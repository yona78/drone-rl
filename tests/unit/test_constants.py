"""Unit tests for drone_rl.constants module."""

from drone_rl.constants import (
    ALPHA_DEFAULT,
    CELL_COLORS,
    COLOR_BUILDING,
    COLOR_CROSSWIND,
    COLOR_EMPTY,
    COLOR_GOAL,
    COLOR_START,
    COLOR_TRAP,
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
from drone_rl.types.grid import CellType


class TestRewardSchedule:
    """Verify reward values match PRD §4.1 exactly."""

    def test_reward_schedule_matches_prd(self) -> None:
        assert REWARD_GOAL == 100.0
        assert REWARD_STEP == -1.0
        assert REWARD_BUILDING_COLLISION == -10.0
        assert REWARD_TRAP_HIT == -100.0
        assert REWARD_CROSSWIND == -10.0


class TestColors:
    """Verify color constants are defined for all cell types."""

    def test_colors_defined_for_all_celltypes(self) -> None:
        for ct in CellType:
            assert ct in CELL_COLORS, f"Missing color for {ct}"

    def test_color_values(self) -> None:
        assert COLOR_EMPTY == "white"
        assert COLOR_START == "green"
        assert COLOR_GOAL == "gold"
        assert COLOR_BUILDING == "gray"
        assert COLOR_TRAP == "red"
        assert COLOR_CROSSWIND == "dodger blue"


class TestGridLimits:
    """Verify grid limits are reasonable."""

    def test_grid_limits_are_reasonable(self) -> None:
        assert GRID_WIDTH_MAX >= GRID_WIDTH_DEFAULT
        assert GRID_HEIGHT_MAX >= GRID_HEIGHT_DEFAULT
        assert GRID_WIDTH_DEFAULT > 0
        assert GRID_HEIGHT_DEFAULT > 0


class TestHyperparameterDefaults:
    """Verify all 8 hyperparameter defaults exist."""

    def test_all_constants_defined(self) -> None:
        assert ALPHA_DEFAULT == 0.1
        assert GAMMA_DEFAULT == 0.99
        assert EPSILON_DEFAULT == 1.0
        assert EPSILON_DECAY_DEFAULT == 0.995
        assert EPSILON_MIN_DEFAULT == 0.01
        assert MAX_STEPS_DEFAULT == 500
        assert TOTAL_EPISODES_DEFAULT == 1000
        assert RANDOM_SEED_DEFAULT == 42

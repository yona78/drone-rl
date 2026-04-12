"""Unit tests for drone_rl.types.agent module."""

from drone_rl.types.agent import (
    ALL_ACTIONS,
    Action,
    AgentState,
    TerminalReason,
)
from drone_rl.types.grid import Coordinate


class TestAction:
    """Tests for Action enum."""

    def test_action_enum_members(self) -> None:
        assert Action.UP.value == "up"
        assert Action.DOWN.value == "down"
        assert Action.LEFT.value == "left"
        assert Action.RIGHT.value == "right"

    def test_action_enum_has_four_directions(self) -> None:
        assert len(Action) == 4

    def test_action_string_values(self) -> None:
        values = {a.value for a in Action}
        assert values == {"up", "down", "left", "right"}

    def test_all_actions_list(self) -> None:
        assert len(ALL_ACTIONS) == 4
        assert ALL_ACTIONS == [
            Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT,
        ]


class TestTerminalReason:
    """Tests for TerminalReason enum."""

    def test_terminal_reason_values(self) -> None:
        assert TerminalReason.GOAL_REACHED.value == "goal_reached"
        assert TerminalReason.TRAP_HIT.value == "trap_hit"
        assert TerminalReason.MAX_STEPS.value == "max_steps"

    def test_terminal_reason_has_three_members(self) -> None:
        assert len(TerminalReason) == 3


class TestAgentState:
    """Tests for AgentState dataclass."""

    def test_agentstate_creation(self) -> None:
        state = AgentState(
            position=Coordinate(row=0, col=0),
            accumulated_reward=0.0,
            step_count=0,
            is_done=False,
        )
        assert state.position == Coordinate(row=0, col=0)
        assert state.accumulated_reward == 0.0
        assert state.step_count == 0
        assert state.is_done is False
        assert state.terminal_reason is None

    def test_agentstate_steps_increment(self) -> None:
        state = AgentState(
            position=Coordinate(row=0, col=0),
            accumulated_reward=0.0,
            step_count=0,
            is_done=False,
        )
        state.step_count += 1
        assert state.step_count == 1

    def test_agentstate_with_terminal_reason(self) -> None:
        state = AgentState(
            position=Coordinate(row=4, col=4),
            accumulated_reward=85.0,
            step_count=15,
            is_done=True,
            terminal_reason=TerminalReason.GOAL_REACHED,
        )
        assert state.is_done is True
        assert state.terminal_reason == TerminalReason.GOAL_REACHED

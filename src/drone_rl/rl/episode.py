"""
Training episode runner for the 2D Drone Pathfinding RL simulation.

Provides run_step (single timestep) and run_episode (full loop).
Goal reward is applied directly — no double-counting with step penalty.

Reference: CODE_PLAN section 11, PRD section 4.1 (Review Point #8).
"""

from __future__ import annotations

import random as _random_module

from ..types.agent import AgentState, TerminalReason
from ..types.grid import CellType, GridState
from ..types.rl import EpisodeRecord, Hyperparameters, QTable, RewardConfig
from .bellman import bellman_update
from .environment import apply_action
from .policy import select_action
from .rewards import compute_reward


def run_step(
    agent: AgentState,
    grid: GridState,
    table: QTable,
    hp: Hyperparameters,
    rewards: RewardConfig,
    rng: _random_module.Random,
    action: Action | None = None,
) -> tuple[AgentState, QTable]:
    """
    Execute a single timestep: select action, move, reward, update Q.

    Goal reward uses ``rewards.goal_reached`` directly (+100), with
    NO step penalty stacked on top (Review Point #8).

    Input Data: agent state, grid, Q-table, hyperparams, rewards, RNG.
    Output Data: (updated AgentState, updated QTable).
    """
    row, col = agent.position.row, agent.position.col

    # 1. Select action (if not provided, use epsilon-greedy with local RNG)
    if action is None:
        action = select_action(table, row, col, hp.epsilon, rng)

    # 2. Apply movement physics
    next_pos = apply_action(agent.position, action, grid)
    next_cell = grid.get_cell_type(next_pos.row, next_pos.col)

    # 3. Check terminal conditions
    is_goal = next_pos == grid.goal_pos
    is_trap = next_cell == CellType.TRAP
    at_max_steps = agent.step_count >= hp.max_steps_per_episode - 1
    is_done = is_goal or is_trap or at_max_steps

    # 4. Compute reward — goal handled directly, no double-counting
    immediate_reward = rewards.goal_reached if is_goal else compute_reward(next_cell, rewards)

    # 5. Bellman Q-table update
    table = bellman_update(
        table,
        row,
        col,
        action,
        immediate_reward,
        next_pos.row,
        next_pos.col,
        is_done,
        hp,
    )

    # 6. Build new agent state
    terminal_reason = None
    if is_done:
        if is_goal:
            terminal_reason = TerminalReason.GOAL_REACHED
        elif is_trap:
            terminal_reason = TerminalReason.TRAP_HIT
        else:
            terminal_reason = TerminalReason.MAX_STEPS

    new_agent = AgentState(
        position=next_pos,
        accumulated_reward=agent.accumulated_reward + immediate_reward,
        step_count=agent.step_count + 1,
        is_done=is_done,
        terminal_reason=terminal_reason,
    )
    return new_agent, table


def run_episode(
    grid: GridState,
    table: QTable,
    hp: Hyperparameters,
    rewards: RewardConfig,
    rng: _random_module.Random,
) -> tuple[QTable, EpisodeRecord]:
    """
    Run a full episode from start until terminal or max steps.

    Input Data: grid, Q-table, hyperparams, rewards, local RNG.
    Output Data: (updated QTable, EpisodeRecord).
    """
    agent = AgentState(
        position=grid.start_pos,
        accumulated_reward=0.0,
        step_count=0,
        is_done=False,
    )

    while not agent.is_done:
        agent, table = run_step(agent, grid, table, hp, rewards, rng)

    record = EpisodeRecord(
        episode=0,  # Caller sets the actual episode number
        total_reward=agent.accumulated_reward,
        steps=agent.step_count,
        terminal_reason=agent.terminal_reason or TerminalReason.MAX_STEPS,
        epsilon=hp.epsilon,
    )
    return table, record

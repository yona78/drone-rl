"""
Reward calculator for the 2D Drone Pathfinding RL simulation.

Maps each CellType to its exact reward value from PRD section 4.1.
Goal reward is handled separately in run_step() to avoid double-counting.

Reference: CODE_PLAN section 8, PRD section 4.1 (MANDATORY values).
"""

from __future__ import annotations

from ..types.grid import CellType
from ..types.rl import RewardConfig


def compute_reward(cell_type: CellType, config: RewardConfig) -> float:
    """
    Map a cell type to its reward value.

    Maps PRD section 4.1 exact values. Goal is handled separately in
    run_step() to avoid double-counting (Review Point #8).

    All CellType values are included in the reward_map dict.

    Input Data: cell_type (CellType enum), config (RewardConfig).
    Output Data: float reward value.
    """
    reward_map: dict[CellType, float] = {
        CellType.EMPTY: config.empty_step,  # -1.0
        CellType.START: config.empty_step,  # -1.0 (start = normal step)
        CellType.GOAL: config.goal_reached,  # +100.0 (fallback)
        CellType.BUILDING: config.building_collision,  # -10.0
        CellType.TRAP: config.trap_hit,  # -100.0
        CellType.CROSSWIND: config.crosswind_penalty,  # -10.0
    }
    return reward_map.get(cell_type, 0.0)

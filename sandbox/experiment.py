
import os
import random
import sys

# Add the src directory to the path so we can import drone_rl
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from drone_rl.rl.base import GridEnvironment
from drone_rl.rl.bellman import compute_q_update
from drone_rl.rl.policy import select_action
from drone_rl.rl.qtable import best_action, get_q, init_qtable, max_q, set_q
from drone_rl.types.agent import ALL_ACTIONS
from drone_rl.types.grid import CellType, Coordinate, GridState
from drone_rl.types.rl import RewardConfig


def run_simple_experiment():
    print("--- Starting Drone RL Sandbox Experiment ---")

    # 1. Setup a simple 3x3 grid
    # S . .
    # . B .
    # . . G
    grid = GridState(
        rows=3,
        cols=3,
        cells={
            (0, 0): CellType.START,
            (1, 1): CellType.BUILDING,
            (2, 2): CellType.GOAL,
        },
        start_pos=Coordinate(0, 0),
        goal_pos=Coordinate(2, 2),
    )

    reward_config = RewardConfig()
    rng = random.Random(42)
    env = GridEnvironment(grid, reward_config, rng)

    # 2. Initialize Q-Table
    q_table = init_qtable(grid)

    # 3. Simple training loop (10 episodes)
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.5

    print(f"Training for 10 episodes (epsilon={epsilon})...")

    for ep in range(1, 11):
        state = env.reset()
        done = False
        total_reward = 0
        steps = 0

        while not done and steps < 20:
            row, col = state.position.row, state.position.col

            # Select action
            action = select_action(q_table, row, col, epsilon, rng)

            # Step environment
            next_state, reward, done = env.step(action)
            next_row, next_col = next_state.position.row, next_state.position.col

            # Update Q-Value
            current_q = get_q(q_table, row, col, action)
            max_next_q = max_q(q_table, next_row, next_col) if not done else 0.0

            new_q = compute_q_update(current_q, reward, max_next_q, alpha, gamma)
            set_q(q_table, row, col, action, new_q)

            state = next_state
            total_reward += reward
            steps += 1

        print(f"Episode {ep}: steps={steps}, total_reward={total_reward:.1f}")

    print("\nFinal Q-Values for Start State (0,0):")
    for action in ALL_ACTIONS:
        q_val = get_q(q_table, 0, 0, action)
        print(f"  {action.value}: {q_val:.4f}")

    print("\nBest action from (0,0):", best_action(q_table, 0, 0).value)
    print("--- Experiment Complete ---")

if __name__ == "__main__":
    run_simple_experiment()

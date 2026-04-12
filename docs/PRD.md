# Product Requirements Document
## 2D Drone Pathfinding Reinforcement Learning Simulation

**Version:** 1.00 | **Document Owner:** Product Management | **Date:** April 12, 2026

**Workflow Reference:** PRD → PLAN → TODO → Development

---

## 1. Project Overview & Context

### 1.1 Problem Statement

Students, educators, and AI practitioners struggle to understand reinforcement learning because the learning process is typically opaque. Most RL implementations use neural networks (DQN) that function as "black boxes," hiding the internal state updates and learned value distributions. While powerful for production systems, this opacity makes learning difficult for educational purposes.

There is a clear market need for transparent, interactive RL educational tools that expose every internal state, action, reward, and learned value in real time, transforming an otherwise opaque training process into an inspectable, hands-on learning experience.

### 1.2 Solution Overview

The 2D Drone Pathfinding Reinforcement Learning Simulation is an interactive desktop application that demonstrates how a software-based drone agent can autonomously discover an optimal path on a two-dimensional grid environment. The simulation places a drone at a designated starting cell (Point A) and tasks it with reaching a designated destination cell (Point B) while navigating around hazards, obstacles, and environmental disturbances.

The core engine uses a Q-Table (tabular reinforcement learning), storing all state-action value estimates explicitly in a lookup table indexed by discrete grid coordinates and discrete action choices, with no neural network approximation. This is a non-negotiable architectural constraint that defines the educational character of the product.

### 1.3 Target Audience & Market

- **Primary:** University students and educators teaching reinforcement learning theory
- **Secondary:** Hobbyists and self-taught AI practitioners seeking hands-on RL experimentation
- **Tertiary:** Researchers analyzing parameter sensitivity in tabular RL
- **Market Context:** Educational software for computer science departments; aligns with coursework in algorithms, AI, and machine learning.

---

## 2. Objectives, KPIs & Acceptance Criteria

### 2.1 Primary Objectives

1. Provide a transparent, educational simulation of tabular Q-learning that exposes all internal states and updates.
2. Enable users to visually inspect policy formation through live convergence graphs, Q-value heatmaps, and episode statistics.
3. Support interactive environment design and custom obstacle placement.
4. Deliver reproducible training and evaluation through JSON-based configuration and policy export/import.
5. Facilitate parameter sensitivity analysis through batch training runs and result visualization.

### 2.2 Key Performance Indicators (KPIs)

| KPI | Target | Measurement |
|-----|--------|-------------|
| **Convergence Speed** | 500–1000 episodes for typical maze | Measured on standard test scenarios |
| **Policy Success Rate** | ≥90% on learned policy | Evaluation runs post-training |
| **UI Responsiveness** | <50 ms frame time during training | Frame rate monitoring |
| **Code Coverage** | ≥85% minimum | CI/CD test report |
| **Parameter Sweep Coverage** | All documented hyperparameters tested | Parameter sensitivity analysis notebook |
| **User Documentation Completeness** | 100% of public API documented | Docstring and README coverage |

### 2.3 Acceptance Criteria

- All three specific test scenarios (Section 11.2) execute successfully and produce expected learning curves.
- Convergence graphs, episode statistics, and Q-value heatmaps render accurately in real time.
- Obstacle colors (gray, red, blue) and reward values match specification exactly.
- Bellman update equation implemented precisely as defined in Section 5.3.
- Q-table policies can be saved and loaded reproducibly.
- All hyperparameters (α, γ, ε) are exposed via UI and respond to user input.
- Minimum 85% test coverage achieved with TDD red-green-refactor workflow.
- Zero hardcoded configuration values; all parameters externalized to JSON config files.
- Comprehensive parameter sensitivity analysis results in accompanying Jupyter notebook.
- Nielsen's 10 Usability Heuristics applied to UI/UX design (documented in separate design doc).

---

## 3. Functional Requirements

### 3.1 Environment & Objective

The environment consists of a finite, discrete two-dimensional grid. The drone agent starts each training and evaluation episode at Point A and must reach Point B. Movement occurs in cardinal directions (up, down, left, right) one cell per timestep. The episode ends when the drone reaches the goal, falls into a trap, or exceeds a configurable maximum step count.

**Inputs to Environment:**
- Grid dimensions (width, height)
- Start position (Point A)
- Goal position (Point B)
- Obstacle positions and types
- Random seed for reproducibility

**Outputs from Environment:**
- Observations (drone state: x, y coordinates)
- Reward signal (immediate scalar feedback)
- Episode termination signal
- Transition metadata (obstacle type hit, collision, etc.)

### 3.2 Interactive Graphical User Interface

The application provides a fully interactive graphical user interface built with tkinter for local desktop execution. The interface includes a built-in environment editor. Users can:

- Place, move, and delete obstacles on any tile of the grid using point-and-click controls on the canvas.
- Reposition the start cell (Point A) and goal cell (Point B).
- Resize the grid (within practical limits; see Section 8).
- Save and load custom environment layouts as JSON files on the local filesystem.
- Pause, resume, step through, or reset episodes at any time via control buttons.
- Save and load trained Q-table policies as JSON files for reproducible evaluation.

**Architectural Constraint (§4 SDK Architecture):** The GUI is a thin presentation layer that delegates all business logic to an SDK module. The GUI never contains state management, reward calculations, Q-learning updates, or collision detection. All such logic is encapsulated in a `drone_rl.sdk` module accessible via well-defined interfaces.

### 3.3 Live Data Visualization

The interface continuously renders live data visualizations alongside the simulation using matplotlib and tkinter canvases. These include:

- **Convergence graph:** Cumulative reward per episode with a moving average overlay (plotted in real time using matplotlib).
- **Episode length chart:** Steps taken per episode with moving average.
- **Episode statistics panel:** Live display of current episode number, total reward, steps, terminal outcome, and current exploration rate.
- **Q-value heatmap overlay:** Optional visual overlay of the maximum Q-value per cell, rendered on the grid canvas to help the user inspect policy formation.
- **Policy arrow overlay:** Optional directional-arrow overlay on the grid canvas showing the greedy action (`argmax Q(s,·)`) for every visited state. Arrows are drawn as small triangles or chevrons inside each cell pointing in the direction of the best action. This overlay can be toggled independently of the heatmap.
- **Canvas legend:** A persistent legend panel (rendered on or beside the grid canvas) mapping each cell color to its meaning: White = Empty, Green = Start, Gold/Yellow = Goal, Gray = Building, Red = Trap, Blue = Crosswind. The legend also shows the drone marker icon and any active overlay indicators (heatmap gradient scale, arrow meaning).

### 3.4 Obstacle Catalog

There are three obstacle types in the environment. Each is rendered with a distinct color and produces a distinct game-mechanical effect on the drone:

- **Buildings — Gray color.** Blocks movement / causes collision. The drone cannot enter a building tile; the attempted action is rejected and a collision penalty is applied.
- **Traps — Red color.** Ends the run / failure. Stepping onto a trap immediately terminates the current episode with a large negative penalty.
- **Crosswinds — Blue color.** Alters movement / adds penalty. Stepping into a crosswind tile pushes the drone one cell in the wind's configured direction and incurs an additional cost. Each crosswind tile has a fixed direction (North, South, East, or West) assigned at environment creation time and stored in `config/setup.json`. If the drift would push the drone out of bounds or into a Building, the drone remains on the crosswind tile (drift is cancelled but the penalty still applies). Wind direction per tile is configurable in the environment editor and persisted in layout JSON files.

| Obstacle   | Color | Penalty     | Behavior                                                                          |
|------------|-------|-------------|-----------------------------------------------------------------------------------|
| Buildings  | Gray  | -10 points  | Blocks movement / causes collision. Drone cannot occupy this tile.                |
| Traps      | Red   | -100 points | Ends the run / failure. Episode terminates immediately upon entry.                |
| Crosswinds | Blue  | -10 points  | Pushes drone 1 cell in configured wind direction; penalty applied even if drift is blocked.|

### 3.5 Interactive Control Features

Users can configure and run training sessions with the following controls exposed in the GUI:

- **Learning rate (α):** Slider or numeric input, range [0.01, 1.0].
- **Discount factor (γ):** Slider or numeric input, range [0.0, 0.99].
- **Exploration rate (ε):** Slider or numeric input, range [0.0, 1.0]; optional decay schedule via checkbox.
- **Episodes:** Numeric input for training run length.
- **Max steps per episode:** Numeric input to prevent infinite loops.
- **Random seed:** Numeric input for reproducibility.
- **Environment editor:** Point-and-click grid editor for placing obstacles, start, and goal.
- **Policy management:** Load/save buttons for Q-table files.
- **Playback controls:** Play, pause, step, reset, and speed adjustment buttons.

---

## 4. Non-Functional Requirements

### 4.1 SDK Architecture & Business Logic Separation

**Requirement (§4):** All business logic must be encapsulated in an SDK module (`drone_rl.sdk`) with well-defined public interfaces. The GUI and CLI frontends delegate entirely to the SDK:

- **State Management:** Grid state, drone position, obstacle positions managed by SDK.
- **Reward Calculation:** All reward function logic isolated in `sdk.reward_calculator` module.
- **Q-Learning Engine:** Bellman update, epsilon-greedy policy, Q-table management in `sdk.qlearning` module.
- **Environment Simulation:** Episode step execution, collision detection, termination checks in `sdk.environment` module.
- **Policy Management:** Q-table serialization, loading, and evaluation in `sdk.policy` module.

The GUI is a thin wrapper that calls SDK methods and updates display elements. No state is held in GUI code beyond canvas positions and widget configurations.

### 4.2 Code Quality & File Size Constraints

**Requirement (§3.2):** All source files, including test files, must not exceed 150 lines of code per file. This constraint enforces modular, focused design:

- Split large modules into single-responsibility components.
- Test files cover individual functions/classes, not entire packages.
- Document this constraint in project README and CI/CD checks.

### 4.3 Test-Driven Development & Coverage

**Requirement (§6):** TDD workflow is mandatory:

1. **Red:** Write failing test that specifies expected behavior.
2. **Green:** Implement minimal code to pass the test.
3. **Refactor:** Improve code while maintaining test pass.

**Coverage Target:** Minimum 85% statement coverage across all modules (excluding `__main__` entry points and visualization code). CI/CD pipeline must fail the build if coverage drops below 85%.

**Edge Cases:** All edge cases must be documented in test comments and represented in test suites:
- Empty grid (no obstacles)
- Unreachable goal (completely blocked)
- Start position = goal position
- Grid boundaries and out-of-bounds moves
- Crosswind stacking (multiple winds on same tile)
- Zero learning rate, zero exploration rate, zero discount factor

### 4.4 Configuration Management

**Requirement (§7):** No hardcoded values in source code. All configurable parameters externalized:

- **Config Files:** JSON-based configuration files for environment defaults, hyperparameter ranges, and visualization settings.
- **Versioning:** Config files are versioned alongside code; breaking changes trigger version bumps.
- **Examples:** Provide `.config-example.json` and `.env-example` templates for users to copy and customize.
- **Runtime Override:** CLI and GUI allow runtime parameter overrides of config file values.

Example config structure:
```json
{
  "grid": {
    "default_width": 10,
    "default_height": 10,
    "max_width": 20,
    "max_height": 20
  },
  "hyperparameters": {
    "alpha": 0.1,
    "gamma": 0.95,
    "epsilon": 0.1
  },
  "rewards": {
    "goal": 100,
    "empty_step": -1,
    "building_collision": -10,
    "trap_hit": -100,
    "crosswind": -10
  }
}
```

### 4.5 Package Management & Dependency Management

**Requirement (§8.1):** The `uv` package manager is mandatory for dependency management. The project must include:

- **pyproject.toml:** Defines project metadata, dependencies, build backend, and entry points.
- **uv.lock:** Lock file ensuring reproducible builds across environments.
- **No pip:** All package installation via `uv`, never `pip`.

### 4.6 Version Numbering

**Requirement (§8.1):** Version numbering follows semantic versioning with fixed-width format: `X.YY` (e.g., `1.00`, `1.01`, `2.00`).

- Initial release: `1.00`
- Patch updates (bug fixes, docs): increment YY (e.g., `1.01`, `1.02`)
- Minor updates (new features): increment X and reset YY (e.g., `2.00`)
- Major breaking changes: increment X and reset YY (e.g., `3.00`)

### 4.7 ISO/IEC 25010 Software Quality Characteristics

The product must adhere to ISO/IEC 25010 quality model:

- **Functional Suitability:** All specified functional requirements met; no missing features.
- **Reliability:** Minimum 85% test coverage; graceful error handling for invalid inputs.
- **Usability:** Nielsen's 10 Heuristics applied (documented separately); accessible UI controls.
- **Performance:** UI frame time <50 ms; policy evaluation completes in <5 seconds per 100 episodes.
- **Maintainability:** Modular SDK architecture; clear separation of concerns; documented extension points.
- **Portability:** Cross-platform tkinter GUI; runs on macOS, Linux, Windows with Python 3.9+.
- **Security:** No SQL injection, no arbitrary code execution; JSON config parsing is strict.

### 4.8 User Interface & Usability (Nielsen's 10 Heuristics)

The UI design adheres to Nielsen's 10 Usability Heuristics:

1. **Visibility of system status:** Real-time episode counter, reward display, current epsilon shown on screen.
2. **Match between system and real world:** Use domain language (drone, grid, obstacles, Q-table, reward).
3. **User control and freedom:** Pause, resume, reset, step buttons; undo obstacle placement (clear and redraw).
4. **Consistency and standards:** Consistent button layouts, color coding (gray=building, red=trap, blue=wind).
5. **Error prevention:** Disable invalid actions (e.g., place start on obstacle); warn on large grids.
6. **Error recovery:** Clear error messages; option to reload last saved policy on crash.
7. **Flexibility and efficiency:** Keyboard shortcuts for power users; batch training mode for parameter sweeps.
8. **Aesthetic and minimalist design:** Clean canvas, uncluttered controls, subtle grid lines.
9. **Help and documentation:** Inline help tooltips; extensive README and docstrings.
10. **Help and error messages:** Human-readable error messages; suggested corrective actions.

### 4.9 Extensibility & Plugin Architecture

**Requirement (§12):** The SDK must be extensible for future enhancements:

**Extension Points:**
- **Reward Functions:** Pluggable reward function interface allowing custom reward schedules.
- **Obstacle Types:** Registry-based obstacle system allowing new obstacle classes without modifying core logic.
- **Visualization:** Abstract visualization interface enabling new chart types and analysis tools.
- **Learning Algorithms:** SDK designed to support future algorithms (e.g., SARSA, Actor-Critic) alongside Q-Learning.

**Documentation:** Each extension point documented with:
- Interface specification (input types, return types, exceptions)
- Example implementation
- Integration checklist

---

## 5. Algorithm Description & Theoretical Background

### 5.1 Tabular Q-Learning Overview

Q-Learning is a model-free, off-policy, value-based reinforcement learning algorithm. In its tabular form, the agent maintains an explicit table Q(s, a) that records the estimated long-term value of taking action a in state s. The agent updates this table after every interaction with the environment using the temporal-difference error between its current estimate and a one-step bootstrap target.

### 5.2 Exploration vs. Exploitation

A central challenge of reinforcement learning is balancing exploration (trying new actions in order to discover better long-term strategies) against exploitation (taking the action currently believed to be best in order to maximize known reward). Our simulation uses an epsilon-greedy policy: with probability epsilon the agent chooses a random action (exploration), and with probability (1 − epsilon) it chooses the action with the highest Q-value for the current state (exploitation). Epsilon is exposed as a UI hyperparameter and may be decayed over time to favor exploitation as learning progresses.

### 5.3 The Bellman Update Equation

The tabular Q-learning update rule is the discrete-form Bellman equation. After every transition, the Q-table entry for the visited state-action pair is updated as follows:

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ R(s,a) + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

Where the variables are defined as:

| Symbol | Name | Definition |
|--------|------|------------|
| `s` | State | The current discrete cell coordinate of the drone on the 2D grid. |
| `a` | Action | The move chosen by the drone from the set {up, down, left, right}. |
| `s'` | Next State | The cell the drone occupies after performing action a (accounting for collisions and crosswinds). |
| `a'` | Next Action | Any candidate action available from s'; the max operator selects the best one. |
| `α` (alpha) | Learning Rate | A value in (0, 1] that controls how aggressively new estimates overwrite old ones. |
| `R(s,a)` | Reward | The immediate scalar feedback the environment returns after the action (see Section 6). |
| `γ` (gamma) | Discount Factor | A value in [0, 1) that weights the importance of future rewards relative to immediate ones. |
| `Q(s,a)` | Q-Value | The current tabular estimate of the long-term value of taking action a from state s. |

The bracketed quantity `[R(s,a) + γ max Q(s',a') − Q(s,a)]` is the temporal-difference (TD) error. Iterating this update across many episodes drives the Q-table to converge toward the optimal action-value function Q\*, from which the optimal policy is recovered by always selecting argmax Q(s, a).

---

## 6. Reward/Penalty System & Expected Inputs/Outputs

### 6.1 Reward Schedule

The reward function is fully deterministic and is defined by the following exact values, which must be implemented as listed:

- **Goal Reached:** +100 points.
- **Empty tile step penalty:** -1 point.
- **Building (Gray) collision penalty:** -10 points.
- **Trap (Red) penalty:** -100 points (ends episode).
- **Crosswind (Blue) penalty:** -10 points.

| Event                      | Value       | Description                                                               |
|----------------------------|-------------|---------------------------------------------------------------------------|
| Goal Reached               | +100 points | Drone successfully arrives at Point B; episode ends in success.           |
| Empty Tile Step            | -1 point    | Standard movement penalty encouraging shortest paths.                     |
| Building (Gray) Collision  | -10 points  | Drone attempts to enter a building tile; movement is blocked.             |
| Trap (Red) Hit             | -100 points | Catastrophic failure; episode terminates immediately.                     |
| Crosswind (Blue) Penalty   | -10 points  | Drone enters a wind tile; movement is altered and penalty is applied.     |

### 6.2 Inputs

All learning hyperparameters are exposed to the user through the graphical interface and may be adjusted before or between training runs:

- **Learning rate (α):** Controls the step size of every Q-table update. Adjustable via slider.
- **Discount factor (γ):** Controls how strongly future rewards influence the current value estimate. Adjustable via slider.
- **Exploration rate (ε):** The epsilon-greedy exploration probability, optionally with a decay schedule. Adjustable via slider.
- Number of training episodes, maximum steps per episode, and a random seed for reproducibility.
- The grid layout itself, including the placement of the start, goal, buildings, traps, and crosswinds, edited interactively in the environment editor.

### 6.3 Outputs

The simulation continuously produces the following outputs in real time and persists them to the local filesystem:

- **Real-time visual simulation:** The drone visibly moves across the grid canvas, tracing the path from Point A to Point B during each episode.
- **Live convergence graph:** A matplotlib figure displaying cumulative reward per episode with moving average updated after each episode.
- **Live episode statistics:** On-screen display of current episode number, total reward, steps taken, terminal outcome (GOAL/TRAP/MAX_STEPS), and current exploration rate.
- **Q-value heatmap overlay:** Optional canvas overlay rendering the maximum Q-value per cell with color gradients.
- **Policy arrow overlay:** Optional canvas overlay showing greedy-action arrows (`argmax Q(s,·)`) per visited cell.
- **Canvas legend:** Persistent legend mapping cell colors to meanings and showing overlay indicator scales.
- **Policy files:** The trained Q-table can be exported and loaded as a JSON file, enabling reproducible evaluation and transfer to new environments. File path defaults to `policies/` directory in the working directory.
- **Episode logs:** A CSV log of all episodes (episode number, total reward, steps, terminal reason, epsilon) is saved to `logs/` directory for offline analysis.

---

## 7. Parameter Sensitivity Analysis & Research Methodology

### 7.1 Parameter Sensitivity Study

To support the research and analysis requirement (§9), a comprehensive parameter sensitivity analysis must be conducted:

**Hyperparameters Under Study:**
- Learning rate α: test {0.01, 0.05, 0.1, 0.5, 1.0}
- Discount factor γ: test {0.0, 0.5, 0.9, 0.95, 0.99}
- Exploration rate ε: test {0.0, 0.05, 0.1, 0.2, 0.5}
- Epsilon decay (if enabled): test {0.995, 0.99, 0.98}

**Measurement Methodology:**
1. For each hyperparameter combination, run at least 5 independent training runs on standard test environment (10×10 grid with maze).
2. Record convergence speed (episodes to reach 90% success rate), final policy success rate (%, n=100 evaluation episodes), and final Q-table entropy.
3. Identify parameter ranges that yield stable, fast convergence.
4. Document hyperparameter interactions (e.g., high α with high γ can cause instability).

### 7.2 Results Documentation & Visualization

**Deliverable:** A Jupyter notebook (`analysis/parameter_sensitivity.ipynb`) containing:

- Heatmaps of convergence speed vs. (α, γ) pairs
- Box plots of final success rate across hyperparameter ranges
- Time series plots of convergence trajectories for selected parameter sets
- Statistical summary (mean, std, min, max for each parameter)
- Recommended hyperparameter ranges for pedagogical scenarios vs. research scenarios

**Quality Visualizations:**
- High-contrast colors, clear axis labels, legend on every figure
- Source data tables embedded in notebook cells for reproducibility
- Written interpretation of each result (what does this heatmap tell us?)

---

## 8. Constraints, Limitations & Alternatives

### 8.1 The Curse of Dimensionality

Tabular Q-learning suffers from the well-known **curse of dimensionality**. Because every state-action pair requires its own explicit entry in the Q-table, the memory footprint grows linearly with the number of states multiplied by the number of actions. For a 2D grid this means memory grows with `width × height × |A|`, and any extension to richer state representations (orientation, velocity, fuel, multiple drones) would multiply this further.

As a direct consequence, the grid size in this product must be moderately sized to prevent memory exhaustion and to ensure that the Q-table can be visited frequently enough to actually converge within a reasonable number of episodes. The interface enforces a soft upper bound on grid dimensions (≤20×20 for practical learning) and warns the user when configurations begin to approach impractical sizes.

### 8.2 Comparison with Deep Q-Networks (DQN) and Justification

An obvious modern alternative to tabular Q-learning is the Deep Q-Network (DQN), which replaces the lookup table with a neural network function approximator that maps states to Q-values. DQN scales gracefully to high-dimensional and continuous state spaces (e.g., raw pixels) and is the de facto choice for complex RL problems.

Despite this, **Tabular Q-learning was chosen over DQN** for this product because it is **transparent, easier to debug, and not a "black box,"** making it better for educational demonstration. Every learned value lives in an inspectable table that can be rendered, exported, and stepped through cell-by-cell. Updates can be hand-traced against the Bellman equation. There are no opaque weight matrices, no minibatch sampling, no target networks, and no instability surprises rooted in nonlinear function approximation.

The pedagogical clarity of seeing exactly what the agent has learned, and exactly how each update changed it, is the central value proposition of this product — and that clarity would be lost if the engine were a neural network. The trade-off is acceptable: the product intentionally restricts itself to moderately sized grids, which is where the tabular approach excels and where the educational payoff is greatest.

### 8.3 Additional Constraints

- Movement is restricted to discrete cardinal moves; no diagonal movement, no continuous control.
- The environment is fully observable; the agent always knows its exact (x, y) coordinate.
- Stochasticity is limited to the epsilon-greedy exploration policy and crosswind drift effects.
- Rewards are dense (every step yields feedback), which is required for tabular Q-learning to converge in a reasonable number of episodes.
- File size constraint: all source files ≤150 lines (§3.2).
- Configuration files must be JSON; no YAML, INI, or proprietary formats.

---

## 9. Assumptions, Dependencies & Out-of-Scope

### 9.1 Assumptions

- Users have a basic understanding of grid coordinates (x, y) and cardinal directions.
- Python 3.9+ is available in the target environment.
- tkinter is available on the target platform (included with most Python distributions).
- Users have write permissions to the working directory for saving policies and logs.
- The grid size does not exceed 20×20 cells during normal operation.
- Training episodes are deterministic given a fixed random seed.

### 9.2 Dependencies

**Runtime:**
- Python 3.9+
- matplotlib (for live convergence graphs)
- tkinter (for GUI; standard library)
- numpy (for efficient array operations, if added)

**Development:**
- pytest (test framework)
- pytest-cov (coverage measurement)
- mypy (optional static type checking)
- black (code formatting; optional)
- uv (package manager; mandatory)

**Build:**
- pyproject.toml (PEP 517/518 compliance)
- uv.lock (reproducible builds)

### 9.3 Out-of-Scope

The following features are explicitly out of scope for v1.00:

- 3D environments or continuous state spaces
- Multiple simultaneous drones (multi-agent RL)
- Neural network function approximation (DQN, DQN variants)
- Distributed training across multiple machines
- Real-time video export of training runs
- Mobile or web-based UI (desktop only)
- Integration with external RL frameworks (e.g., OpenAI Gym, Stable-Baselines3)
- Custom reward functions defined by users (hardcoded reward values only)
- Support for stochastic environments (transitions are deterministic given actions)

---

## 10. Timeline & Milestones

| Phase | Deliverable | Duration | Target Date |
|-------|-------------|----------|-------------|
| **Phase 1: Planning** | PLAN document, architecture design, test strategy | 1 week | Week 1 |
| **Phase 2: SDK Development** | Core SDK modules: environment, Q-learning, reward, policy | 3 weeks | Week 4 |
| **Phase 3: GUI & Visualization** | tkinter interface, live graphs, heatmap renderer | 2 weeks | Week 6 |
| **Phase 4: Testing & Coverage** | Unit tests (TDD), integration tests, 85%+ coverage | 2 weeks | Week 8 |
| **Phase 5: Parameter Analysis** | Sensitivity analysis runs, Jupyter notebook results | 1 week | Week 9 |
| **Phase 6: Documentation & Polish** | README, docstrings, config examples, edge cases | 1 week | Week 10 |
| **Phase 7: Validation & Release** | Full test scenario validation, final QA, v1.00 release | 1 week | Week 11 |

**Total Expected Duration:** 11 weeks

**Key Milestones:**
- Week 4: SDK feature complete, 70%+ test coverage
- Week 6: GUI functional with live training visualization
- Week 8: Minimum 85% test coverage achieved; zero failing tests
- Week 10: All documentation complete; parameter sensitivity results published
- Week 11: v1.00 release ready; all acceptance criteria met

---

## 11. Success Criteria & Test Scenarios

### 11.1 Overall Success Criteria

The product is considered successful when, given a fixed environment and a reasonable hyperparameter configuration, the trained Q-table consistently produces a policy that reaches Point B with a high success rate, achieves a stable upward trend in the convergence graph, and visibly favors safe routes over catastrophic ones. The interface must remain responsive during training and must accurately render all live visualizations without lag or graphical artifacts.

### 11.2 Specific Test Scenarios

The following three test scenarios must be passed to validate that the learning engine, the reward system, and the visualization stack are functioning correctly:

1. **Direct Route (empty grid):** On a grid with no obstacles, the drone must learn a straight-line (or near-straight Manhattan) path from Point A to Point B. The agent should converge to a policy that balances the **-1 step penalties** by minimizing the number of steps taken to reach the goal.

2. **Maze Navigation (gray walls obstructing):** On a grid populated with **gray Building tiles** arranged as a maze, the drone must learn to navigate the perimeter and corridors to avoid the **-10 collision penalties**. A successful run produces a path that does not repeatedly bump into building walls.

3. **Risk Aversion (red traps near shortest path):** On a grid where **red Traps** are deliberately placed adjacent to or along the shortest geometric route, the drone must learn a slightly longer route that avoids the catastrophic **-100 penalty**. The agent should sacrifice a few **-1 step penalties** in exchange for safety, demonstrating that the discounted value function correctly captures risk.

### 11.3 Acceptance

Acceptance of the product requires that all three scenarios above are reproducible from a clean install, that the convergence graphs visually demonstrate learning, and that the obstacle colors, reward values, and Bellman update behavior all match this specification exactly.

### 11.4 Test Coverage & CI/CD Requirements

- Minimum 85% line coverage across all SDK modules (measured by pytest-cov).
- All three test scenarios automated in test suite with deterministic assertions.
- CI/CD pipeline runs full test suite and coverage report on every commit.
- Build fails if coverage drops below 85% or any test fails.
- Edge cases documented and tested (see Section 4.3).

---

## 12. Building Blocks & Component Design

The product is organized into focused, single-responsibility modules. Each component defines clear Input/Output/Setup expectations:

### 12.1 SDK Components

**`drone_rl.sdk.environment`**
- **Input:** Grid dimensions, start/goal positions, obstacle positions, random seed
- **Output:** Observations (position), rewards, termination signals
- **Setup:** Obstacle registry, collision detection rules

**`drone_rl.sdk.qlearning`**
- **Input:** Experience tuple (s, a, r, s'), hyperparameters (α, γ, ε)
- **Output:** Updated Q-table, action selection decision
- **Setup:** Q-table initialization, epsilon decay schedule

**`drone_rl.sdk.reward`**
- **Input:** Environment state, action taken, transition result
- **Output:** Scalar reward value
- **Setup:** Reward schedule (values per Section 6)

**`drone_rl.sdk.policy`**
- **Input:** Q-table data structure, destination path
- **Output:** JSON-serialized policy or loaded Q-table
- **Setup:** File I/O handlers, serialization format

**`drone_rl.gui`**
- **Input:** User interactions (button clicks, canvas edits), SDK outputs
- **Output:** Rendered UI, display updates, file system writes
- **Setup:** tkinter canvas, matplotlib figure integration

---

## 13. Extensibility Points (§12)

Future enhancements must integrate through documented extension points:

1. **Custom Reward Functions:** Subclass `RewardFunction` interface; register in reward factory.
2. **New Obstacle Types:** Extend `Obstacle` base class; define color, penalty, behavior; register in obstacle registry.
3. **Visualization Plugins:** Implement `VisualizationPlugin` interface; add to visualizer queue.
4. **Future RL Algorithms:** Refactor learning engine interface to support SARSA, Actor-Critic alongside Q-Learning.

### 13.1 Middleware Architecture & Lifecycle Hooks (§12.1)

The SDK implements a **Middleware Architecture** with explicit **Lifecycle Hooks** to safely allow plugins to inject custom logic at key points:

- **`before_episode_start(episode_num: int) -> None`** — Called at the start of each episode; allows plugins to reset state, log setup, configure environment.
- **`after_step_update(step_record: StepRecord) -> None`** — Called after each Q-table update; allows plugins to collect statistics, validate updates, modify behavior dynamically.
- **`on_episode_complete(episode_record: EpisodeRecord) -> None`** — Called when an episode ends (goal/trap/max_steps); allows plugins to react to termination, adjust hyperparameters, trigger analysis.
- **`on_training_pause() -> None`** — Called when training is paused; allows plugins to save intermediate results, generate checkpoints.
- **`on_training_resume() -> None`** — Called when training resumes; allows plugins to reload state, validate consistency.

Middleware is registered via `sdk.register_middleware(middleware_instance)` and is invoked in FIFO order. Plugins MUST NOT modify shared state directly; they communicate via hooks and return values.

Each extension point documented in `docs/EXTENSIONS.md` with code examples.

---

## 14. Additional Resources & References

### 14.1 Companion Algorithm Document

A dedicated algorithm PRD exists in `docs/PRD_rl_algorithm.md` containing:
- Deep dive into tabular Q-learning theory
- Convergence proofs and theoretical properties
- Comparison with function approximation methods
- Hyperparameter impact on convergence

Refer to that document for mathematical rigor; this PRD focuses on software engineering and product perspective.

### 14.2 Documentation Structure

```
├── README.md                    (Quick start, installation, overview)
├── docs/
│   ├── ARCHITECTURE.md          (SDK design, module structure)
│   ├── PRD_rl_algorithm.md      (Q-Learning theory and algorithms)
│   ├── EXTENSIONS.md            (Extension points, plugin development)
│   ├── TESTING.md               (Test strategy, edge cases, TDD workflow)
│   └── USABILITY.md             (Nielsen heuristics, UI/UX decisions)
├── analysis/
│   └── parameter_sensitivity.ipynb  (Jupyter notebook with analysis results)
├── config/
│   ├── config.json              (Default configuration)
│   └── config-example.json      (Example for users to copy)
└── tests/
    ├── test_environment.py
    ├── test_qlearning.py
    ├── test_reward.py
    └── ...
```

### 14.3 References

- **Bellman, R. (1957).** Dynamic Programming. Princeton University Press.
- **Watkins, C. J. (1989).** Learning from Delayed Rewards. PhD thesis, Cambridge University.
- **Sutton, R. S., & Barto, A. G. (2018).** Reinforcement Learning: An Introduction (2nd ed.). MIT Press.
- **Nielsen, J. (1994).** Usability Engineering. Morgan Kaufmann. (10 Usability Heuristics)
- **ISO/IEC 25010:2023.** Software and Data Quality Requirements and Evaluation.
- **PEP 517, 518, 621.** Python packaging standards.
- **uv Documentation:** https://github.com/astral-sh/uv

---

## 15. Final Checklist (§17)

Before release as v1.00, verify:

- [ ] All three test scenarios pass with expected convergence behavior
- [ ] Bellman equation implemented exactly as specified in Section 5.3
- [ ] All reward values match Section 6 (goal=+100, step=-1, building=-10, trap=-100, wind=-10)
- [ ] Obstacle colors correct (Building=Gray, Trap=Red, Crosswind=Blue)
- [ ] Q-table policy save/load functional with JSON format
- [ ] UI responsive (<50 ms frame time); no lag during training
- [ ] Live convergence graph, episode statistics, heatmap all rendering correctly
- [ ] Minimum 85% test coverage achieved (verified by pytest-cov in CI)
- [ ] TDD red-green-refactor workflow followed for all features
- [ ] All source files ≤150 lines; test files ≤150 lines
- [ ] No hardcoded configuration values; all in JSON config or .env-example
- [ ] SDK architecture enforced: all business logic in `drone_rl.sdk`, GUI is thin wrapper
- [ ] pyproject.toml and uv.lock present; `uv` used exclusively for dependency management
- [ ] Version number set to 1.00 (not 1.0)
- [ ] README complete with installation instructions, quick start, API overview
- [ ] Docstrings on all public functions and classes
- [ ] Parameter sensitivity analysis notebook complete with visualizations
- [ ] Nielsen's 10 Heuristics documented in UI design; accessibility considerations noted
- [ ] Extension points documented in `docs/EXTENSIONS.md` with examples
- [ ] ISO/IEC 25010 characteristics reviewed; no critical deficiencies
- [ ] Edge cases tested and documented (empty grid, unreachable goal, etc.)
- [ ] No SQL injection, arbitrary code execution, or security vulnerabilities
- [ ] Cross-platform testing on macOS, Linux, Windows (or documented compatibility)
- [ ] All workflow steps documented: PRD → PLAN → TODO → Development
- [ ] Reference to companion algorithm document (`docs/PRD_rl_algorithm.md`) in place

---

*— End of Document —*
*v1.00 | Dr. Yoram Segal Guidelines Compliance | April 12, 2026*

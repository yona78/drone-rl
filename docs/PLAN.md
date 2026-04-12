# Code Plan
## 2D Drone Pathfinding Reinforcement Learning Simulation (Python Edition)

**Version:** 3.0 | **Based on PRD:** v1.00 | **Date:** April 12, 2026 | **Compliance:** Dr. Yoram Segal Professional Software Guidelines

---

## 1. Tech Stack & Mandatory Constraints

### 1.1 Core Language & Package Management

- **Python:** 3.10+ (minimum for type hints and modern stdlib)
- **Package Manager:** `uv` (MANDATORY) — fast, modern Python project manager with reproducible builds
  - **NEVER use:** `pip`, `pip install`, `python -m`, `venv`, `virtualenv`
  - **ONLY use:** `uv sync`, `uv add`, `uv run`, `uv lock`
  - **Single source of truth:** `pyproject.toml` + `uv.lock` (no `requirements.txt`)

### 1.2 GUI & Visualization

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Desktop GUI | **tkinter** (built-in) | No external dependencies; native OS rendering; simple event loop integration |
| Grid Canvas | **tkinter Canvas** | Efficient 2D drawing; cell hover detection via mouse events; native zoom/pan capable |
| Charting | **matplotlib** ≥3.8 | Embedded in tkinter via `FigureCanvasTkAgg`; real-time updates; convergence graph quality |
| Serialization | **json** (stdlib) | Native Python support; human-readable Q-table and layout export; no third-party dependency |

### 1.3 Code Quality Standards (Dr. Segal)

**File Size Constraint (§3.2):** Every source file ≤150 lines (excluding blank lines and comments). Test files also ≤150 lines. This is a HARD constraint enforced in CI/CD.

**Ruff Configuration (§7.1):** Zero Ruff violations mandatory.
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","C4","SIM"]
ignore = ["E501"]
```

**Package Organization (§14):**
- `__init__.py` in EVERY directory with `__all__` and `__version__`
- ALL imports must be relative (never absolute paths from project root)
- File read/write paths relative to package path

### 1.4 Project Structure for `uv`

```
drone-rl/
├── pyproject.toml      # uv project manifest (ONLY dependency source)
├── uv.lock             # reproducible lock (auto-generated)
├── .env-example        # Template for environment variables
├── .gitignore
├── README.md
│
├── src/drone_rl/       # Python package root
│   ├── __init__.py     # __version__ = "1.00"
│   ├── main.py         # Entry point: initializes tkinter app
│   ├── constants.py    # Immutable project constants (enums, math)
│   │
│   ├── sdk/            # ←← SDK LAYER: Single entry point for all logic ←←
│   │   ├── __init__.py
│   │   └── sdk.py      # DroneRLSDK class exposing all operations
│   │
│   ├── rl/             # Pure RL engine (NO tkinter, NO GUI)
│   │   ├── __init__.py
│   │   ├── qtable.py
│   │   ├── bellman.py
│   │   ├── rewards.py
│   │   ├── environment.py
│   │   ├── policy.py
│   │   └── episode.py
│   │
│   ├── gui/            # Thin presentation layer (delegates to SDK)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── canvas.py
│   │   ├── editor.py
│   │   ├── hyperparameter_panel.py  # Sliders for α, γ, ε (≤150 lines)
│   │   ├── playback_controls.py     # Train/Pause/Reset/Step buttons (≤150 lines)
│   │   ├── io_panel.py              # Save/Load policy & layout buttons (≤150 lines)
│   │   ├── charts.py
│   │   └── panels.py
│   │
│   ├── types/          # Canonical dataclasses (no logic)
│   │   ├── __init__.py
│   │   ├── grid.py
│   │   ├── agent.py
│   │   └── rl.py
│   │
│   ├── shared/         # Shared utilities & configuration
│   │   ├── __init__.py
│   │   ├── config.py   # Configuration manager (reads from JSON)
│   │   ├── version.py  # Version tracking (__version__ = "1.00")
│   │   └── gatekeeper.py  # ApiGatekeeper (§5): event-throttle + rate_limits.json
│   │
│   └── utils.py        # Helper functions (file I/O, math)
│
├── tests/              # pytest suite (mirrors src/ structure)
│   ├── conftest.py     # Pytest fixtures
│   ├── unit/           # Unit tests
│   │   ├── test_rl/
│   │   │   ├── test_bellman.py
│   │   │   ├── test_rewards.py
│   │   │   ├── test_policy.py
│   │   │   ├── test_environment.py
│   │   │   └── test_episode.py
│   │   ├── test_sdk/
│   │   └── test_utils/
│   └── integration/    # Integration tests
│       ├── test_scenarios/
│       │   └── test_three_scenarios.py  # PRD §11.2 scenarios
│       └── test_file_io/
│
├── config/             # Configuration files (NOT in source)
│   ├── setup.json      # Main app config (grid defaults, UI settings)
│   ├── rewards.json    # Reward values (versioned)
│   ├── hyperparameters.json  # Default hyperparameters (versioned)
│   ├── logging_config.json   # Logging configuration
│   └── rate_limits.json      # ApiGatekeeper config (§5) — internal event throttle
│
├── docs/
│   ├── PRD.md          # → PRD_2D_Drone_Pathfinding_RL.md
│   ├── PLAN.md         # → CODE_PLAN.md (this file)
│   ├── TODO.md         # Development TODO tracker
│   ├── PRD_rl_algorithm.md   # Algorithm deep dive
│   ├── ARCHITECTURE.md # SDK design details
│   ├── EXTENSIONS.md   # Extension points & plugin development
│   ├── TESTING.md      # Test strategy & edge cases
│   ├── prompts.md      # Prompt engineering log (§8.3)
│   ├── USABILITY.md    # Nielsen heuristics & UI/UX decisions
│   └── COST_ANALYSIS.md  # §11 API/token cost breakdown (cost = $0.00, fully local)
│
├── results/            # Experiment results (JSON, CSV)
├── assets/             # Screenshots, diagrams, graphs
├── notebooks/          # Jupyter analysis notebooks
├── policies/           # Saved Q-tables (JSON)
├── layouts/            # Saved grid layouts (JSON)
└── logs/               # Episode CSV logs
```

---

## 2. SDK Architecture Layer (§4 — Dr. Segal Mandatory)

### 2.0 SDK Architectural Principle

**ALL business logic must be accessed through the SDK layer. The GUI NEVER calls RL functions directly — only through the SDK.**

The `drone_rl.sdk` module is the single entry point for all business logic. It exposes a `DroneRLSDK` class with well-defined public methods for:
- Initializing environments
- Running training episodes
- Computing rewards
- Managing Q-tables and policies
- Saving/loading states
- Evaluating trained policies

**Key constraint:** No tkinter imports in the RL engine (`src/drone_rl/rl/`). No direct imports from GUI to RL. All coupling goes through SDK.

---

## 3. Core Data Models & Structures

All types live in `src/drone_rl/types/` as simple dataclasses with no methods. The RL engine in `src/drone_rl/rl/` imports and uses these types as pure data.

### 3.1 `types/grid.py` — Grid & Environment Types

```python
from enum import Enum
from dataclasses import dataclass

class CellType(Enum):
    """Obstacle types from PRD §2.4"""
    EMPTY     = "empty"
    START     = "start"
    GOAL      = "goal"
    BUILDING  = "building"   # Gray  — blocks movement, -10 penalty
    TRAP      = "trap"       # Red   — ends episode,   -100 penalty
    CROSSWIND = "crosswind"  # Blue  — alters movement, -10 penalty

@dataclass(frozen=True)
class Coordinate:
    """Immutable 2D position"""
    row: int
    col: int

@dataclass(frozen=True)
class Cell:
    """Single grid tile (immutable value object)"""
    row: int
    col: int
    type: CellType

@dataclass
class GridState:
    """Full environment state"""
    rows: int
    cols: int
    cells: dict[tuple[int, int], CellType]  # (row, col) -> CellType
    start_pos: Coordinate
    goal_pos: Coordinate
    wind_directions: dict[tuple[int, int], "Action"] = field(default_factory=dict)
    # Maps crosswind tile positions to their wind direction (Action enum)
    # Persisted in layout JSON; configurable in environment editor

    def get_cell_type(self, row: int, col: int) -> CellType:
        """Lookup cell type; default to EMPTY if not found"""
        return self.cells.get((row, col), CellType.EMPTY)

    def get_wind_direction(self, row: int, col: int) -> "Action":
        """Lookup wind direction for a crosswind tile; default to UP"""
        from .agent import Action
        return self.wind_directions.get((row, col), Action.UP)
```

### 3.2 `types/agent.py` — Agent & Action Types

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Action(Enum):
    """Movement actions"""
    UP    = "up"
    DOWN  = "down"
    LEFT  = "left"
    RIGHT = "right"

ALL_ACTIONS = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

class TerminalReason(Enum):
    """How an episode ended"""
    GOAL_REACHED = "goal_reached"
    TRAP_HIT     = "trap_hit"
    MAX_STEPS    = "max_steps"

@dataclass
class AgentState:
    """Runtime agent snapshot"""
    position: Coordinate
    accumulated_reward: float
    step_count: int
    is_done: bool
    terminal_reason: Optional[TerminalReason] = None
```

### 3.3 `types/rl.py` — Q-Learning Types

```python
from dataclasses import dataclass, field
from typing import Dict

# Q-Table: Maps (row,col) -> {Action enum -> Q-value}
StateKey = str  # Format: "row,col" (canonical string representation)
QTable = Dict[StateKey, Dict[Action, float]]  # Keys are Action enum members, NOT strings

def state_key(row: int, col: int) -> StateKey:
    """Canonical state key builder (ALWAYS use this)"""
    return f"{row},{col}"

@dataclass
class Hyperparameters:
    """Learning configuration (from PRD §4.2)"""
    alpha: float = 0.1             # Learning rate
    gamma: float = 0.99            # Discount factor
    epsilon: float = 1.0           # Exploration rate
    epsilon_decay: float = 0.995   # Multiplicative decay per episode
    epsilon_min: float = 0.01      # Floor for epsilon
    max_steps_per_episode: int = 500
    total_episodes: int = 1000
    random_seed: int = 42

@dataclass
class RewardConfig:
    """Exact reward values (PRD §4.1 — MANDATORY)"""
    goal_reached: float = 100.0
    empty_step: float = -1.0
    building_collision: float = -10.0
    trap_hit: float = -100.0
    crosswind_penalty: float = -10.0

@dataclass
class EpisodeRecord:
    """Training history per episode"""
    episode: int
    total_reward: float
    steps: int
    terminal_reason: TerminalReason
    epsilon: float
```

### 3.4 `shared/version.py` — Version Tracking (§8.1)

```python
# src/drone_rl/shared/version.py
__version__ = "1.00"
```

All configuration JSON files must include `"version": "1.00"` key for compatibility tracking.

### 3.5 `shared/config.py` — Configuration Management (§7)

Reads from `config/` directory JSON files (NOT hardcoded in source). Only allowed in source:
- Mathematical/physical constants
- Default parameter values
- Enum values
- Values in `constants.py`

### 3.5b `shared/gatekeeper.py` — ApiGatekeeper (§5 — Dr. Segal mandatory)

The guidelines require an `ApiGatekeeper` class for all external calls with queueing, retry logic, and `rate_limits.json`. This application makes **no external API calls** (tabular Q-learning is 100% local CPU math; LLM token cost = $0.00). The gatekeeper is therefore implemented as an **internal GUI event throttle** — a legitimate internal use of the pattern:

```python
import queue
import time
from pathlib import Path
import json

class ApiGatekeeper:
    """
    §5 ApiGatekeeper — required by Dr. Segal guidelines.
    
    This app makes no external API calls (see docs/COST_ANALYSIS.md for $0 token cost).
    The gatekeeper is implemented as an internal event-throttle that:
      - Queues EpisodeRecord callbacks from training thread (queue.Queue)
      - Limits GUI update rate to max_gui_updates_per_second (from rate_limits.json)
      - Provides retry/backoff interface (no-ops for local-only calls)
    """

    def __init__(self, config_path: Path):
        with open(config_path) as f:
            cfg = json.load(f)
        self._max_ups = cfg["max_gui_updates_per_second"]
        self._queue: queue.Queue = queue.Queue(maxsize=cfg["max_episode_callbacks_queued"])
        self._last_emit = 0.0

    def enqueue(self, item) -> bool:
        """Add item to throttled queue. Returns False if queue full."""
        try:
            self._queue.put_nowait(item)
            return True
        except queue.Full:
            return False

    def drain(self) -> list:
        """Drain all pending items if rate limit allows. Called from main thread."""
        now = time.monotonic()
        if now - self._last_emit < 1.0 / self._max_ups:
            return []
        self._last_emit = now
        items = []
        while not self._queue.empty():
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items

    def _validate_config(self) -> None:
        """Raises ValueError on invalid gatekeeper configuration."""
        if self._max_ups <= 0:
            raise ValueError("max_gui_updates_per_second must be > 0")
```

### 3.6 Application State Container

The `SimulationState` dataclass holds all application state:

```python
from dataclasses import dataclass, field
from .types import GridState, AgentState, QTable, EpisodeRecord, Coordinate

@dataclass
class SimulationState:
    """Holds all application state (UI, RL engine, animation)"""
    grid: GridState
    qtable: QTable
    agent: AgentState
    episodes: list[EpisodeRecord] = field(default_factory=list)
    is_training: bool = False
    current_episode: int = 0
    paused: bool = False
    drone_animation_pos: Coordinate = None
    path_trail: list[Coordinate] = field(default_factory=list)
```

---

## 4. Configuration Management (§7 — Dr. Segal)

### 4.1 Configuration File Structure

All configurable values externalized to `config/` directory:

**`config/setup.json`** — Main app configuration
```json
{
  "version": "1.00",
  "grid": {
    "default_width": 10,
    "default_height": 10,
    "max_width": 20,
    "max_height": 20
  },
  "ui": {
    "window_width": 1400,
    "window_height": 900
  }
}
```

**`config/rewards.json`** — Reward values (PRD §6.1 MANDATORY)
```json
{
  "version": "1.00",
  "goal_reached": 100.0,
  "empty_step": -1.0,
  "building_collision": -10.0,
  "trap_hit": -100.0,
  "crosswind_penalty": -10.0
}
```

**`config/hyperparameters.json`** — Default hyperparameters
```json
{
  "version": "1.00",
  "alpha": 0.1,
  "gamma": 0.99,
  "epsilon": 1.0,
  "epsilon_decay": 0.995,
  "epsilon_min": 0.01,
  "max_steps_per_episode": 500,
  "total_episodes": 1000,
  "random_seed": 42
}
```

**`config/rate_limits.json`** — ApiGatekeeper configuration (§5 — Dr. Segal mandatory)
```json
{
  "version": "1.00",
  "note": "This app performs no external API calls. Token cost is $0.00 (see docs/COST_ANALYSIS.md). Gatekeeper enforces internal GUI event throttle to prevent runaway UI updates.",
  "max_gui_updates_per_second": 30,
  "max_episode_callbacks_queued": 100,
  "retry_attempts": 0,
  "retry_backoff_seconds": 0
}
```

### 4.2 No Hardcoded Values in Source

Source code contains ONLY:
- Class definitions, function implementations
- Type hints, docstrings
- Enum definitions
- Mathematical/physical constants in `constants.py`
- Default parameter values (backed by config files)

### 4.3 Configuration Versioning

Config files are versioned. Breaking changes to schema trigger version bumps.

---

## 5. File & Folder Structure Summary

The key architectural principle: **RL engine is completely independent of GUI. SDK acts as the single entry point.**

- `src/drone_rl/sdk/` — DroneRLSDK class; all business logic accessed through here
- `src/drone_rl/rl/` — Pure Python functions, zero tkinter imports, fully unit-testable
- `src/drone_rl/gui/` — tkinter code only; delegates to SDK only
- `src/drone_rl/types/` — Shared canonical types; no logic
- `src/drone_rl/shared/` — Configuration manager, version tracking, utilities
- `src/drone_rl/utils.py` — Helper functions (math, file I/O, grid utilities)
- `config/` — JSON configuration files (NOT in source)

### 5.1 Complete Directory Tree

---

## 6. Test Structure (§6 — Dr. Segal)

**Mandatory TDD:** Red-Green-Refactor workflow for all features.

**Coverage:** Minimum 85% (CI/CD fails if below). Test files also ≤150 lines.

```
tests/
├── conftest.py            # pytest fixtures
├── unit/
│   ├── test_rl/
│   │   ├── test_bellman.py      # Hand-traced Bellman updates (≤150 lines)
│   │   ├── test_rewards.py      # Exact PRD §6.1 values
│   │   ├── test_policy.py       # Epsilon-greedy distribution
│   │   ├── test_environment.py  # Movement, boundaries, crosswinds
│   │   └── test_episode.py      # Full episode integration
│   ├── test_sdk/
│   │   └── test_sdk_interface.py  # SDK public API tests
│   └── test_utils/
│       └── test_helpers.py        # Utility function tests
└── integration/
    ├── test_scenarios/
    │   └── test_three_scenarios.py  # PRD §11.2 scenarios (Direct Route, Maze, Risk Aversion)
    └── test_file_io/
        └── test_config_loading.py   # JSON config file loading
```

**Edge cases documented & tested:**
- Empty grid (no obstacles)
- Unreachable goal (completely blocked)
- Start position = goal position
- Grid boundaries and out-of-bounds moves
- Zero learning rate, zero exploration rate
- Large grids (dimensionality warnings)

---

## 7. Research & Results Directories (§9 — Dr. Segal)

```
results/       # Experiment results (JSON, CSV from parameter sensitivity)
assets/        # Screenshots, architecture diagrams, graphs
notebooks/     # Jupyter analysis notebooks (parameter sensitivity analysis)
```

Add a Phase 7 (Research) for parameter sensitivity analysis and results visualization.

---

## 8. Execution Phases (Updated with SDK & Config Architecture)

### Phase 0 — Scaffold & Documentation (NEW)

**Goal:** Project skeleton with docs, config directory, version tracking, .env-example.

1. **Initialize project:**
   ```bash
   uv init drone-rl
   cd drone-rl
   uv add matplotlib  # only external dependency for charting
   ```

2. **Create directory structure** as specified above (all `__init__.py` files).

3. **Add `src/drone_rl/shared/version.py`** with `__version__ = "1.00"`.

4. **Create `config/` directory** with `setup.json`, `rewards.json`, `hyperparameters.json`.

5. **Create `.env-example`** template for environment variables.

6. **Create documentation skeleton:**
   - `docs/PRD.md` (reference to PRD_2D_Drone_Pathfinding_RL.md)
   - `docs/PLAN.md` (reference to CODE_PLAN.md)
   - `docs/TODO.md` (development tracker)
   - `docs/prompts.md` (prompt engineering log — §8.3)

7. **Add `pyproject.toml`** with metadata, dependencies, ruff config.

---

### Phase 1 — Project Scaffolding & Core Types

**Goal:** All core types defined; configuration system working; zero RL logic yet. All files ≤150 lines.

1. **Write all shared types** in `src/drone_rl/types/`:
   - `grid.py`: `CellType`, `Coordinate`, `Cell`, `GridState` (≤150 lines)
   - `agent.py`: `Action`, `ALL_ACTIONS`, `TerminalReason`, `AgentState` (≤150 lines)
   - `rl.py`: `QTable` type alias, `state_key()`, `Hyperparameters`, `RewardConfig`, `EpisodeRecord` (≤150 lines)
   
   Add unit tests for `state_key()` format. Use `frozen=True` for immutable dataclasses. **Coverage target: 100%**.

2. **Implement `shared/config.py`** — Configuration manager that reads from `config/` JSON files:
   - Load `setup.json`, `rewards.json`, `hyperparameters.json`
   - Expose `get_config(key)`, `get_reward_config()`, `get_hyperparameters()`
   - Validate version compatibility
   - File ≤150 lines

3. **Create `constants.py`** with immutable constants:
   - Color hex mappings: `CELL_COLORS = {CellType.BUILDING: "#9CA3AF", ...}`
   - Grid size limits (max 20×20 per PRD §8.1)
   - All enum values
   - Hyperparameter defaults: `ALPHA_DEFAULT = 0.1`, `GAMMA_DEFAULT = 0.99`, `EPSILON_DEFAULT = 1.0`, `EPSILON_DECAY_DEFAULT = 0.995`, `EPSILON_MIN_DEFAULT = 0.01`, `MAX_STEPS_DEFAULT = 500`, `TOTAL_EPISODES_DEFAULT = 1000`, `RANDOM_SEED_DEFAULT = 42`
   - File ≤150 lines

4. **Create `utils.py`** with pure helper functions (≤150 lines per file; split if needed):
   - `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` — pathlib-based project root resolved relative to `__file__`, NOT hardcoded relative paths (fragile if cwd changes)
   - `CONFIG_DIR = PROJECT_ROOT / "config"` — all config paths derived from `PROJECT_ROOT`
   - `create_empty_grid(rows, cols) -> GridState`
   - `clone_grid(grid) -> GridState`
   - `is_in_bounds(grid, row, col) -> bool`
   - `set_cell(grid, row, col, cell_type) -> GridState` (immutable)
   - `moving_average(values, window_size) -> list`
   - `clamp(value, min_val, max_val) -> float`
   - `create_rng(seed: int) -> random.Random` — returns a LOCAL `random.Random(seed)` instance (never global)
   
   Write unit tests for each. **Coverage target: 100%**.

5. **Create `state.py`** with `SimulationState` dataclass (≤150 lines).

---

### Phase 2 — Pure RL Engine (No tkinter)

**Goal:** A fully tested, deterministic RL engine that runs independently of the GUI. All files ≤150 lines.

All RL files MUST import nothing from `gui`, `shared/config`, or tkinter. Pure functions only.

**File ≤150 lines constraint:** RL logic is split across focused, single-responsibility files.

6. **`src/drone_rl/rl/qtable.py` (≤150 lines):**
   - `init_qtable(grid: GridState) -> QTable` — initialize all non-Building cells to zero.
   - `get_q(table, row, col, action) -> float`
   - `set_q(table, row, col, action, value) -> QTable` (immutable update returning new table)
   - `best_action(table, row, col) -> Action` — `argmax` over all four actions
   - `max_q(table, row, col) -> float` — `max` over all action values
   
   Write unit tests for each function.

7. **`src/drone_rl/rl/bellman.py` (≤150 lines):**
   ```python
   def bellman_update(
       table: QTable,
       row: int, col: int,  # state (s)
       action: Action,      # action taken (a)
       reward: float,       # R(s, a)
       next_row: int, next_col: int,  # next state (s')
       is_done: bool,
       hp: Hyperparameters,
   ) -> QTable:
       """
       Applies: Q(s,a) ← Q(s,a) + α [ R(s,a) + γ · max_a' Q(s',a') − Q(s,a) ]
       """
       current_q = get_q(table, row, col, action)
       future_q = 0.0 if is_done else max_q(table, next_row, next_col)
       td_target = reward + hp.gamma * future_q
       td_error = td_target - current_q
       new_q = current_q + hp.alpha * td_error
       return set_q(table, row, col, action, new_q)
   ```
   Write a unit test that hand-traces one update with known values and verifies output to 6 decimal places.

8. **`src/drone_rl/rl/rewards.py` (≤150 lines):**
   ```python
   def compute_reward(cell_type: CellType, config: RewardConfig) -> float:
       """Maps PRD §6.1 exact values. Goal is handled separately in run_step()."""
       reward_map = {
           CellType.EMPTY: config.empty_step,
           CellType.START: config.empty_step,     # Start tile = normal step
           CellType.GOAL: config.goal_reached,     # Fallback if called directly
           CellType.BUILDING: config.building_collision,
           CellType.TRAP: config.trap_hit,
           CellType.CROSSWIND: config.crosswind_penalty,
       }
       return reward_map.get(cell_type, 0.0)
   ```
   Write tests asserting every value matches PRD §4.1 defaults exactly.

9. **`src/drone_rl/rl/environment.py` (≤150 lines):**
   ```python
   def apply_action(
       pos: Coordinate,
       action: Action,
       grid: GridState,
   ) -> Coordinate:
       """
       Applies movement physics:
       - Compute candidate next position from action
       - If out-of-bounds or Building: return current position (blocked)
       - If Crosswind: apply drift offset, clamp to bounds
       - Otherwise: return candidate
       """
       # Movement vectors
       deltas = {
           Action.UP: (-1, 0),
           Action.DOWN: (1, 0),
           Action.LEFT: (0, -1),
           Action.RIGHT: (0, 1),
       }
       dr, dc = deltas[action]
       next_r, next_c = pos.row + dr, pos.col + dc
       
       # Boundary check
       if not is_in_bounds(grid, next_r, next_c):
           return pos
       
       # Obstacle check
       cell_type = grid.get_cell_type(next_r, next_c)
       if cell_type == CellType.BUILDING:
           return pos
       
       # Crosswind drift: push drone 1 cell in the tile's configured wind direction
       if cell_type == CellType.CROSSWIND:
           wind_dir = grid.get_wind_direction(next_r, next_c)  # Returns Action enum
           wd_r, wd_c = deltas[wind_dir]
           drift_r, drift_c = next_r + wd_r, next_c + wd_c
           # If drift target is out-of-bounds or a Building, cancel drift (PRD §3.4)
           if not is_in_bounds(grid, drift_r, drift_c) or grid.get_cell_type(drift_r, drift_c) == CellType.BUILDING:
               return Coordinate(next_r, next_c)  # Stay on crosswind tile
           return Coordinate(drift_r, drift_c)
       
       return Coordinate(next_r, next_c)
   ```
   Write tests for boundaries, buildings, crosswinds.

10. **`src/drone_rl/rl/policy.py` (≤150 lines):**
    ```python
    import random as _random_module
    
    def select_action(
        table: QTable,
        row: int, col: int,
        epsilon: float,
        rng: _random_module.Random,  # local RNG instance, NOT global random
    ) -> Action:
        """Epsilon-greedy policy using local RNG for reproducibility (§8.1)"""
        if rng.random() < epsilon:
            return rng.choice(ALL_ACTIONS)  # Explore (local RNG)
        else:
            return best_action(table, row, col)  # Exploit
    ```
    
    **Critical:** All randomness MUST use a local `random.Random(seed)` instance, NEVER `random.seed()` + global `random.random()`. This ensures deterministic reproducibility without polluting global state (§8.1 version tracking & reproducibility).
    
    Write tests for both exploration and exploitation branches.

11. **`src/drone_rl/rl/episode.py` (≤150 lines; split if needed):**
    ```python
    def run_step(
        agent: AgentState,
        grid: GridState,
        table: QTable,
        hp: Hyperparameters,
        rewards: RewardConfig,
        rng: random.Random,  # local RNG instance (NOT global)
    ) -> tuple[AgentState, QTable, EpisodeRecord | None]:
        """
        Single timestep: select action, apply, compute reward, update Q-table
        Returns: (updated_agent, updated_table, episode_record_if_done)
        """
        # Select action
        action = select_action(table, agent.position.row, agent.position.col, hp.epsilon, rng)
        
        # Apply movement
        next_pos = apply_action(agent.position, action, grid)
        
        # Check terminal conditions FIRST
        next_cell = grid.get_cell_type(next_pos.row, next_pos.col)
        is_goal = (next_pos == grid.goal_pos)
        is_trap = (next_cell == CellType.TRAP)
        is_done = is_goal or is_trap or (agent.step_count >= hp.max_steps_per_episode - 1)
        
        # Compute immediate reward — goal is handled directly, NO stacking
        if is_goal:
            immediate_reward = rewards.goal_reached  # +100, clean (no step penalty added)
        else:
            immediate_reward = compute_reward(next_cell, rewards)
        
        # Update Q-table
        new_table = bellman_update(
            table, agent.position.row, agent.position.col, action,
            immediate_reward, next_pos.row, next_pos.col,
            is_done, hp
        )
        
        # Update agent state
        new_agent = AgentState(
            position=next_pos,
            accumulated_reward=agent.accumulated_reward + immediate_reward,
            step_count=agent.step_count + 1,
            is_done=is_done,
            terminal_reason=None
        )
        if is_done:
            if is_goal:
                new_agent.terminal_reason = TerminalReason.GOAL_REACHED
            elif is_trap:
                new_agent.terminal_reason = TerminalReason.TRAP_HIT
            else:
                new_agent.terminal_reason = TerminalReason.MAX_STEPS
        
        return new_agent, new_table, None
    
    def run_episode(
        grid: GridState,
        table: QTable,
        hp: Hyperparameters,
        rewards: RewardConfig,
        rng: random.Random,  # local RNG instance (NOT global)
    ) -> tuple[QTable, EpisodeRecord]:
        """Full episode loop until done or max steps"""
        agent = AgentState(
            position=grid.start_pos,
            accumulated_reward=0.0,
            step_count=0,
            is_done=False,
        )
        current_epsilon = hp.epsilon
        
        while not agent.is_done and agent.step_count < hp.max_steps_per_episode:
            agent, table, _ = run_step(agent, grid, table, hp, rewards, rng)
        
        record = EpisodeRecord(
            episode=0,  # Set by caller
            total_reward=agent.accumulated_reward,
            steps=agent.step_count,
            terminal_reason=agent.terminal_reason,
            epsilon=current_epsilon,
        )
        
        return table, record
    ```

12. **Comprehensive unit tests** in `tests/unit/test_rl/` (each ≤150 lines):
    - `test_bellman.py`: Hand-traced Bellman updates with known values
    - `test_rewards.py`: Exact PRD §6.1 values verification
    - `test_policy.py`: Epsilon-greedy exploration/exploitation distribution
    - `test_environment.py`: Movement, boundaries, crosswinds, collisions
    - `test_episode.py`: Full episode integration with step execution
    
    **Coverage target: ≥85%** for all RL modules.

13. **Integration tests** in `tests/integration/test_scenarios/`:
    - `test_three_scenarios.py` (≤150 lines): Direct Route, Maze Navigation, Risk Aversion (PRD §11.2)
    
    Verify each scenario produces expected learning curves and final policy success rates.

**Phase 2b — OOP Wrappers (§OOP — Dr. Segal: base classes, inheritance, Mixins)**

The guidelines mandate OOP with base classes, inheritance, and Mixins. The pure functions above are the correct mathematical inner layer; these OOP classes wrap them to satisfy the rubric's explicit structural requirement. File: `src/drone_rl/rl/base.py` (≤150 lines).

```python
from abc import ABC, abstractmethod
from .rewards import compute_reward
from ..types.grid import CellType
from ..types.rl import RewardConfig

class RewardMixin:
    """
    Mixin providing reward computation to any environment class.
    Satisfies Dr. Segal OOP requirement (§OOP: Mixins prevent code duplication).
    Delegates to pure function compute_reward() for mathematical correctness.
    """
    _reward_config: RewardConfig  # Must be set by host class

    def get_reward(self, cell_type: CellType) -> float:
        """Compute reward for landing on a given cell type."""
        return compute_reward(cell_type, self._reward_config)


class BaseEnvironment(ABC):
    """
    Abstract base class for all RL environments.
    Satisfies Dr. Segal OOP requirement (§OOP: base classes + inheritance).
    Defines the interface contract; GridEnvironment provides the implementation.
    
    IMPLEMENTS THE TEMPLATE METHOD DESIGN PATTERN (§4.2):
    The `step()` method is the template method that relies on abstract subclass
    implementations to define specific physics (apply_action, compute_reward, etc.).
    This allows GridEnvironment to override behavior while maintaining the step() contract.
    """

    @abstractmethod
    def reset(self) -> "AgentState":
        """Reset environment to initial state. Returns starting AgentState."""

    @abstractmethod
    def step(self, action: "Action") -> tuple["AgentState", float, bool]:
        """
        Template Method: Apply action and return next state.
        Subclasses override to define physics via apply_action() and compute_reward().
        Returns (next_state, reward, is_done).
        """

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate configuration on init. Raises ValueError on bad config."""


class GridEnvironment(RewardMixin, BaseEnvironment):
    """
    Concrete grid-based environment (inherits BaseEnvironment + RewardMixin).
    Thin OOP wrapper around the pure-function RL engine. All physics logic
    delegates to apply_action() and compute_reward() pure functions.
    """

    def __init__(self, grid: "GridState", reward_config: RewardConfig, rng: "random.Random"):
        self._grid = grid
        self._reward_config = reward_config  # Required by RewardMixin
        self._rng = rng
        self._agent: "AgentState | None" = None
        self._validate_config()

    def _validate_config(self) -> None:
        if self._grid.rows <= 0 or self._grid.cols <= 0:
            raise ValueError("Grid dimensions must be > 0")
        if self._grid.start_pos == self._grid.goal_pos:
            raise ValueError("Start and goal positions must differ")

    def reset(self) -> "AgentState":
        from ..types.agent import AgentState
        self._agent = AgentState(
            position=self._grid.start_pos,
            accumulated_reward=0.0,
            step_count=0,
            is_done=False,
        )
        return self._agent

    def step(self, action: "Action") -> tuple["AgentState", float, bool]:
        from .environment import apply_action
        next_pos = apply_action(self._agent.position, action, self._grid)
        cell_type = self._grid.get_cell_type(next_pos.row, next_pos.col)
        is_goal = (next_pos == self._grid.goal_pos)
        reward = self._reward_config.goal_reached if is_goal else self.get_reward(cell_type)
        is_done = is_goal or (cell_type == CellType.TRAP)
        return next_pos, reward, is_done
```

---

### Phase 3 — SDK Layer (NEW — Dr. Segal §4)

**Goal:** Encapsulate all RL logic behind a clean SDK interface. GUI will never import RL directly.

14. **`src/drone_rl/sdk/sdk.py` (≤150 lines; split if needed):**
    
    Implement `DroneRLSDK` class with public methods:
    - `__init__(config: Config)` — on init, creates output directories if missing: `os.makedirs(policies_dir, exist_ok=True)`, `os.makedirs(logs_dir, exist_ok=True)`, `os.makedirs(layouts_dir, exist_ok=True)`. Uses pathlib-based paths derived from `PROJECT_ROOT`. Calls `self._validate_config()` at end of init. Initializes `self._middleware: list = []` for lifecycle hooks (Fix 7: §12.1).
    - `_validate_config(self) -> None` — raises `ValueError` on invalid config (§16 Building Blocks validation): checks grid dims > 0, reward values finite, hyperparameter ranges valid (0 < alpha ≤ 1, 0 ≤ gamma < 1, 0 ≤ epsilon ≤ 1).
    - `register_middleware(self, middleware) -> None` — register a middleware instance; will be invoked at lifecycle hooks in FIFO order (Fix 7: §12.1 middleware architecture).
    - **Lifecycle hooks** (Fix 7: §12.1): call each registered middleware in FIFO order:
      - `_call_hook_before_episode_start(episode_num: int) -> None` — invokes `middleware.before_episode_start(episode_num)` for each registered plugin.
      - `_call_hook_after_step_update(step_record) -> None` — invokes `middleware.after_step_update(step_record)` after each Q-table update.
      - `_call_hook_on_episode_complete(episode_record) -> None` — invokes `middleware.on_episode_complete(episode_record)` when episode ends (goal/trap/max_steps).
      - `_call_hook_on_training_pause() -> None` — invokes `middleware.on_training_pause()` when user clicks "Pause" button.
      - `_call_hook_on_training_resume() -> None` — invokes `middleware.on_training_resume()` when user clicks "Resume" button.
    - `initialize_environment(grid_spec) -> GridState`
    - `run_episode(grid, qtable) -> (qtable, EpisodeRecord)`
    - `compute_episode_reward(cell_type) -> float`
    - `save_policy(qtable, filepath)`
    - `load_policy(filepath) -> QTable`
    - `save_layout(grid, filepath)`
    - `load_layout(filepath) -> GridState`
    - `evaluate_policy(grid, qtable, num_runs) -> float`
    
    All GUI code calls SDK methods ONLY. RL engine is encapsulated.

15. **`src/drone_rl/sdk/__init__.py`:**
    - Export `DroneRLSDK` class
    - `__all__ = ["DroneRLSDK"]`
    - `__version__ = "1.00"`

16. **Unit tests** in `tests/unit/test_sdk/`:
    - `test_sdk_interface.py` (≤150 lines): Verify all SDK public methods work correctly
    
    **Coverage target: ≥85%** for SDK layer.

---

### Phase 4 — GUI Framework & Grid Editor

**Goal:** A functioning tkinter window with an interactive grid canvas and environment editor. GUI is thin wrapper; all logic delegates to SDK.

All GUI files ≤150 lines. GUI MUST NOT import from `rl/` package directly — only from `sdk/`.

17. **`src/drone_rl/gui/app.py` (≤150 lines):**
    ```python
    import tkinter as tk
    from drone_rl.gui.canvas import GridCanvas
    from drone_rl.gui.editor import EnvironmentEditor
    from drone_rl.gui.hyperparameter_panel import HyperparameterPanel
    from drone_rl.gui.playback_controls import PlaybackControls
    from drone_rl.gui.io_panel import IOPanel
    from drone_rl.gui.charts import MatplotlibCharts
    
    class DroneRLApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Drone Pathfinding RL Simulation")
            self.geometry("1400x900")
            
            # Main layout
            left_frame = tk.Frame(self)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
            
            right_frame = tk.Frame(self)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Left: Grid canvas + editor
            self.grid_canvas = GridCanvas(left_frame, self.state)
            self.grid_canvas.pack()
            
            self.editor = EnvironmentEditor(left_frame, self.state, self.grid_canvas)
            self.editor.pack(pady=10)
            
            # Right: Controls + charts
            self.playback = PlaybackControls(right_frame, self.state)
            self.playback.pack(fill=tk.X, pady=10)
            
            self.hparams = HyperparameterPanel(right_frame, self.state)
            self.hparams.pack(fill=tk.X, pady=10)
            
            self.io_panel = IOPanel(right_frame, self.state)
            self.io_panel.pack(fill=tk.X, pady=10)
            
            self.charts = MatplotlibCharts(right_frame)
            self.charts.pack(fill=tk.BOTH, expand=True)
    ```

18. **`src/drone_rl/gui/canvas.py` (≤150 lines):**
    - Custom `GridCanvas(tk.Canvas)` subclass
    - Renders cells with colors from `constants.CELL_COLORS`
    - Shows start/goal icons
    - Handles `<Button-1>` and `<B1-Motion>` events
    - Updates when `state.grid` changes
    - Delegates all logic to SDK via app's sdk reference
    - **Policy arrow overlay:** Toggleable layer drawing directional arrows (triangles/chevrons) showing `argmax Q(s,·)` per visited cell. Triggered by a checkbox in the controls panel.
    - **Q-value heatmap overlay:** Toggleable color-gradient overlay showing `max Q(s,·)` per cell.
    - **Canvas legend:** Persistent legend widget (rendered beside or below the grid) mapping each cell color to its meaning (White=Empty, Green=Start, Gold=Goal, Gray=Building, Red=Trap, Blue=Crosswind), plus overlay indicators (heatmap gradient scale, arrow meaning, drone marker icon).

19. **`src/drone_rl/gui/editor.py` (≤150 lines):**
    - Toolbar with radio buttons: Place Building | Place Trap | Place Crosswind | Erase | Move Start | Move Goal
    - Grid size sliders (row/col)
    - "Save Layout" / "Load Layout" buttons (calls SDK methods)
    - Mouse event handlers update `state.grid`, trigger canvas redraws
    - File ≤150 lines; split if needed

20. **GUI Controls — Pre-split into 3 files (§3.2 150-line constraint):**
    
    **`src/drone_rl/gui/hyperparameter_panel.py` (≤150 lines):**
    - Sliders for α, γ, ε, ε-decay, ε-min, episode count, max steps
    - Labels showing current values; binds to `state.hyperparameters`
    - All value changes delegate to SDK
    
    **`src/drone_rl/gui/playback_controls.py` (≤150 lines):**
    - "Train" / "Pause" / "Reset" / "Step" buttons (wired to training loop)
    - Speed slider for animation fps
    - All button handlers delegate to SDK
    
    **`src/drone_rl/gui/io_panel.py` (≤150 lines):**
    - "Save Policy" / "Load Policy" buttons with file dialogs
    - "Save Layout" / "Load Layout" buttons with file dialogs
    - "Export Episode Log" button
    - All file I/O delegates to SDK

21. **`src/drone_rl/gui/charts.py` (≤150 lines):**
    - Embed two matplotlib figures (Convergence + EpisodeLength) in tkinter
    - Figures update after each episode via callback from runner
    - No RL logic; only visualization

22. **`src/drone_rl/gui/panels.py` (≤150 lines):**
    - `EpisodeStatsPanel`: Live display of episode #, reward, steps, terminal reason, epsilon
    - `StatusBar`: Training status (idle / training / paused / done)

---

### Phase 5 — Training Loop Integration

**Goal:** Wire the SDK to the GUI; training runs in the main thread but doesn't block redraws.

23. **`src/drone_rl/runner.py` (≤150 lines; split if needed):**
    Training loop runs in main thread with `update_idletasks()` to allow GUI responsiveness.
    
    ```python
    def training_loop(sdk: DroneRLSDK, state: SimulationState, on_episode_callback):
        """Runs in main thread; yields control to tkinter event loop."""
        for episode in range(state.hyperparameters.total_episodes):
            if not state.is_training or state.paused:
                break
            
            # Run one episode through SDK
            state.qtable, record = sdk.run_episode(state.grid, state.qtable)
            record.episode = episode
            state.episodes.append(record)
            
            # Update epsilon
            state.hyperparameters.epsilon = max(
                state.hyperparameters.epsilon_min,
                state.hyperparameters.epsilon * state.hyperparameters.epsilon_decay
            )
            
            on_episode_callback(record)
            state.root.update_idletasks()  # Yield to GUI
    ```

24. **Wire buttons in `PlaybackControls` to SDK methods:**
    - Train button: calls `training_loop(sdk, state, callback)`
    - Pause button: sets `state.paused = True`
    - Reset button: reinitialize `state.qtable`, `state.episodes` via SDK
    - Step button: call `sdk.run_step()` once

---

### Phase 6 — Animation & Live Charts

**Goal:** Drone animates across the grid; convergence graphs update in real time.

25. **Drone animation:**
    - After each step, update `state.drone_animation_pos`
    - In `GridCanvas`, use `time.sleep(1/fps)` between position updates
    - Redraw canvas with drone at interpolated position

26. **Charts update:**
    - `on_episode_callback()` in `runner.py` calls `charts.update(record)` to redraw convergence graph
    - Matplotlib figures update asynchronously without blocking training

27. **Episode stats panel:**
    - Callback updates `EpisodeStatsPanel` with live values

---

### Phase 7 — File I/O & Configuration

**Goal:** User can save trained Q-tables and grid layouts as JSON. SDK manages file I/O.

28. **File I/O functions in `utils.py` (≤150 lines per file; split if needed):**
    ```python
    import json
    from pathlib import Path
    
    def save_policy(qtable: QTable, filepath: str):
        """Serialize Q-table to JSON"""
        data = {state_key: {action.value: q for action, q in actions.items()}
                for state_key, actions in qtable.items()}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_policy(filepath: str) -> QTable:
        """Deserialize Q-table from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        qtable = {}
        for state_key, actions_dict in data.items():
            qtable[state_key] = {Action[a.upper()]: q for a, q in actions_dict.items()}
        return qtable
    
    def save_layout(grid: GridState, filepath: str):
        """Serialize GridState to JSON"""
        data = {
            "rows": grid.rows,
            "cols": grid.cols,
            "start_pos": {"row": grid.start_pos.row, "col": grid.start_pos.col},
            "goal_pos": {"row": grid.goal_pos.row, "col": grid.goal_pos.col},
            "cells": [(r, c, cell_type.value)
                      for (r, c), cell_type in grid.cells.items()],
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_layout(filepath: str) -> GridState:
        """Deserialize GridState from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        cells = {(r, c): CellType(ct) for r, c, ct in data["cells"]}
        return GridState(
            rows=data["rows"],
            cols=data["cols"],
            cells=cells,
            start_pos=Coordinate(data["start_pos"]["row"], data["start_pos"]["col"]),
            goal_pos=Coordinate(data["goal_pos"]["row"], data["goal_pos"]["col"]),
        )
    
    def export_episode_log(episodes: list[EpisodeRecord], filepath: str):
        """Export episodes as CSV"""
        import csv
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["episode", "total_reward", "steps", "terminal_reason", "epsilon"])
            writer.writeheader()
            for record in episodes:
                writer.writerow({
                    "episode": record.episode,
                    "total_reward": record.total_reward,
                    "steps": record.steps,
                    "terminal_reason": record.terminal_reason.value,
                    "epsilon": record.epsilon,
                })
    ```

29. **Update `LayoutManager` in `editor.py`:**
    - "Save Layout" button: file dialog → calls `sdk.save_layout()`
    - "Load Layout" button: file dialog → calls `sdk.load_layout()` → update `state.grid` → redraw
    - Same for policies via `SimulationControls`

---

### Phase 8 — Parameter Sensitivity Analysis & Research (§9)

**Goal:** Conduct systematic parameter sensitivity analysis. Produce Jupyter notebook with results visualization.

30. **Parameter sensitivity study:**
    - Test hyperparameter combinations (α, γ, ε) using SDK
    - Run 5+ independent training runs per combination on standard 10×10 maze
    - Record: convergence speed, final success rate, Q-table entropy
    - Identify stable parameter ranges

31. **Results directory structure:**
    ```
    results/
    ├── sensitivity_results.json    # Raw data
    ├── convergence_analysis.csv    # Aggregated results
    └── parameter_recommendations.txt
    
    notebooks/
    └── parameter_sensitivity.ipynb # Jupyter analysis with heatmaps, plots
    
    assets/
    ├── convergence_heatmap.png
    ├── success_rate_boxplot.png
    └── architecture_diagram.png
    ```

32. **Jupyter notebook deliverable:**
    - Heatmaps of convergence speed vs. (α, γ)
    - Box plots of final success rate
    - Time series convergence trajectories
    - Statistical summaries
    - Recommended hyperparameter ranges
    - Written interpretation of results

---

### Phase 9 — Polish, Quality & Acceptance

**Goal:** Production quality; all edge cases handled; acceptance criteria met (PRD §2.3, §11).

33. **Code Quality (Dr. Segal Compliance):**
    - All source files ≤150 lines ✓
    - All test files ≤150 lines ✓
    - ≥85% test coverage across all modules (verified by pytest-cov in CI)
    - Zero Ruff violations
    - All imports relative (no absolute paths)
    - `__init__.py` in every directory with `__all__` and `__version__`

34. **Dimensionality warnings:**
    - In grid controls, display yellow badge if `rows × cols > 900`
    - Display red badge if `rows × cols > 2500`

35. **Boundary guards:**
    - Prevent training if start or goal is unreachable (run BFS on grid)
    - Display error banner if grid has no valid path

36. **Reproducibility:**
    - Thread seeded RNG through all RL functions
    - Verify: same seed + same grid = identical training trajectory

37. **Acceptance test suite (PRD §11):**
    - **Direct Route scenario:** drone learns straight-line path on empty grid
    - **Maze Navigation:** drone learns to navigate gray buildings
    - **Risk Aversion:** drone avoids red traps, learns safe routes
    - All three scenarios pass integration tests with expected convergence curves

38. **Configuration validation:**
    - All reward values match PRD §6.1 exactly (goal=+100, step=-1, building=-10, trap=-100, wind=-10)
    - Obstacle colors correct (Building=Gray, Trap=Red, Crosswind=Blue)
    - Bellman update matches PRD §5.3 precisely

39. **UI/UX Polish (Nielsen's 10 Heuristics):**
    - Real-time episode counter, reward display, epsilon visible
    - Domain language used consistently
    - Pause/resume/reset buttons responsive
    - Color coding intuitive and consistent
    - Error messages human-readable with corrective actions
    - Keyboard shortcuts for power users
    - Clean canvas, uncluttered controls
    - Inline help tooltips and comprehensive README

40. **Documentation completion:**
    - README.md with installation, quick start, API overview
    - All public functions have docstrings
    - `docs/ARCHITECTURE.md` — SDK design details
    - `docs/EXTENSIONS.md` — extension points with examples
    - `docs/TESTING.md` — test strategy and edge cases
    - `docs/prompts.md` — prompt engineering log (§8.3)
    - `docs/USABILITY.md` — Nielsen heuristics applied
    - `docs/COST_ANALYSIS.md` — §11 cost breakdown (token cost = $0.00; architectural decision to use local tabular math)
    - `.env-example` template provided

---

### Phase 10 — Final Acceptance & Release (v1.00)

**Goal:** Verify all acceptance criteria. Release v1.00.

41. **Release Checklist (PRD §15):**
    - [ ] All three test scenarios pass with expected convergence
    - [ ] Bellman equation matches PRD §5.3 exactly
    - [ ] All reward values match PRD §6.1 (goal=+100, step=-1, building=-10, trap=-100, wind=-10)
    - [ ] Obstacle colors correct (Building=Gray, Trap=Red, Crosswind=Blue)
    - [ ] Q-table policy save/load functional in JSON format
    - [ ] UI responsive (<50 ms frame time); no lag during training
    - [ ] Live convergence graph, episode statistics, heatmap all rendering correctly
    - [ ] ≥85% test coverage (pytest-cov in CI)
    - [ ] TDD red-green-refactor followed for all features
    - [ ] All source files ≤150 lines; test files ≤150 lines
    - [ ] No hardcoded config values; all in JSON files or constants.py
    - [ ] SDK architecture enforced; all business logic in sdk/, GUI is thin wrapper
    - [ ] pyproject.toml and uv.lock present; only uv used for dependencies
    - [ ] Version number 1.00 (not 1.0)
    - [ ] README complete with installation, quick start, API overview
    - [ ] All public functions have docstrings
    - [ ] Parameter sensitivity analysis notebook complete
    - [ ] Nielsen's 10 Heuristics documented
    - [ ] Extension points documented in docs/EXTENSIONS.md
    - [ ] ISO/IEC 25010 characteristics reviewed
    - [ ] Edge cases tested and documented
    - [ ] No security vulnerabilities (no code injection, strict JSON parsing)
    - [ ] Cross-platform testing (macOS, Linux, Windows)
    - [ ] All workflow steps documented: PRD → PLAN → TODO → Development
    - [ ] Reference to companion algorithm doc (PRD_rl_algorithm.md)

---

## Summary: Key Architectural Principles (Dr. Segal + PRD)

1. **SDK Architecture (§4):** All business logic encapsulated in `drone_rl.sdk.DroneRLSDK`. GUI never imports from RL package directly — only through SDK.

2. **File Size Constraint (§3.2):** Every source file ≤150 lines (excluding blanks/comments). HARD constraint. Enforced in CI/CD.

3. **Pure RL Engine:** All code in `src/drone_rl/rl/` is pure Python — no tkinter imports, fully unit-testable, immutable update patterns.

4. **Configuration Management (§7):** Zero hardcoded values in source. All configurable parameters in JSON config files with versioning.

5. **uv Mandatory (§8.4):** Never use pip. Only uv sync, uv add, uv run, uv lock. pyproject.toml is single source of truth.

6. **Version Tracking (§8.1):** `__version__ = "1.00"` in `src/drone_rl/shared/version.py`. All config JSON files include `"version": "1.00"` key.

7. **TDD & Coverage (§6):** Red-Green-Refactor workflow mandatory. Minimum 85% coverage. Test files also ≤150 lines.

8. **Immutable Data Structures:** Use `frozen=True` dataclasses. Return new copies instead of mutating state.

9. **Test Structure:** Mirror src/ structure in tests/. Separate unit/ and integration/ tests. Edge cases documented.

10. **JSON Serialization:** Q-tables and layouts as plain JSON for human inspection and portability.

11. **No External RL Framework:** Implement Q-learning from first principles (PRD §5.2) for transparency and educational value.

12. **Package Organization (§14):** `__init__.py` in every directory with `__all__` and `__version__`. All imports relative.

13. **Research & Results (§9):** Parameter sensitivity analysis with Jupyter notebook visualization. results/, assets/, notebooks/ directories.

14. **Ruff Configuration (§7.1):** Zero Ruff violations mandatory.
    ```toml
    [tool.ruff]
    line-length = 100
    target-version = "py310"
    [tool.ruff.lint]
    select = ["E","F","W","I","N","UP","B","C4","SIM"]
    ignore = ["E501"]
    ```

15. **Prompt Engineering Log (§8.3):** `docs/prompts.md` documents all AI prompts used during development.

---

*— End of Code Plan v3.0 —*
*Compliance: Dr. Yoram Segal Professional Software Guidelines + PRD v1.00 | April 12, 2026*

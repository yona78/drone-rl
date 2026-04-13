# 2D Drone Pathfinding RL Simulation

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![uv](https://img.shields.io/badge/pkg-uv-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

A local-only desktop application that trains a drone agent to navigate a 2D grid using tabular Q-Learning. Built with Python and tkinter, compliant with Dr. Yoram Segal Professional Software Guidelines v1.00.

## Overview

The simulation presents a configurable grid environment where a drone (agent) learns optimal paths from a start position to a goal using the Q-Learning reinforcement learning algorithm. The agent encounters three obstacle types and must learn to navigate around buildings, avoid traps, and compensate for crosswind drift.

All computation is performed locally using pure tabular math. No neural networks, no external APIs, no cloud services. Token cost: $0.00.

## Features

- Tabular Q-Learning with configurable hyperparameters (alpha, gamma, epsilon)
- Interactive tkinter GUI with real-time training visualization
- Three obstacle types: Buildings (gray), Traps (red), Crosswinds (blue)
- Drag-and-drop grid editor for custom layouts
- Q-value heatmap overlay and policy arrow display
- Real-time convergence chart (matplotlib embedded)
- Save/load Q-tables (policies) and grid layouts as JSON
- Episode CSV logging for post-analysis
- Fully reproducible via local RNG seeding

## Requirements

- Python 3.10 or higher
- `uv` package manager (mandatory)
- tkinter (typically bundled with Python; on Linux may require `sudo apt install python3-tk`)

## Installation

```bash
git clone <repo-url> drone-rl
cd drone-rl
uv sync
```

## Running the App

```bash
uv run python -m drone_rl.main
```

## Running Tests

```bash
uv run pytest
uv run pytest -v
uv run pytest tests/unit/test_rl/test_grid_types.py -v
```

## Obstacle Types

| Type | Color | Reward | Behavior |
|------|-------|--------|----------|
| Building | Gray | -10 | Blocks movement; agent bounces back |
| Trap | Red | -100 | Ends the episode immediately |
| Crosswind | Blue | -10 | Drifts agent in configured wind direction |

## Reward Values

| Event | Reward | Source |
|-------|--------|--------|
| Reach goal | +100 | PRD section 4.1 |
| Empty step | -1 | Encourages shortest path |
| Building collision | -10 | Discourages wall-hugging |
| Trap hit | -100 | Terminal penalty |
| Crosswind tile | -10 | Penalty for wind zones |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Toggle Pause / Resume training |
| `Ctrl+S` | Save current policy to JSON |
| `Ctrl+L` | Load policy from JSON |
| `Ctrl+R` | Reset Q-table and episode log |
| `Ctrl+E` | Export episode log to CSV |
| `Delete` | Clear selected grid cell to Empty |
| Mouse drag | Paint multiple cells in one gesture |

## Development

### Lint & Format

```bash
# Check all files (ruff)
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

### Tests & Coverage

```bash
# Full test suite
uv run pytest

# With coverage report
uv run pytest --cov=src/drone_rl --cov-report=term-missing

# Single module
uv run pytest tests/unit/test_rl/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# Coverage gate (fails below 85%)
uv run pytest --cov=src/drone_rl --cov-fail-under=85
```

### Line-count audit (150-line rule §3.2)

```bash
find src/ tests/ -name "*.py" | xargs wc -l | sort -n | tail -20
```

### Run the parameter sensitivity notebook

```bash
uv run jupyter nbconvert --to notebook --execute \
  notebooks/parameter_sensitivity.ipynb \
  --output notebooks/parameter_sensitivity_executed.ipynb
```

## Project Structure

```
drone-rl/
  src/drone_rl/       Python package root
    types/            Canonical dataclasses (no logic)
    rl/               Pure RL engine (no GUI imports)
    sdk/              SDK layer (single entry point for business logic)
    gui/              Thin tkinter presentation layer
    shared/           Configuration, version, gatekeeper
    constants.py      Immutable project constants
    utils.py          Helper functions
    main.py           Application entry point
  tests/
    unit/             Fast isolated unit tests
    integration/      Multi-module integration tests
  config/             JSON configuration files
  docs/               Project documentation
  notebooks/          Jupyter parameter sensitivity analysis
  results/            Sensitivity analysis output JSON
  assets/             Exported notebook HTML
  policies/           Saved Q-tables (JSON)
  layouts/            Saved grid layouts (JSON)
  logs/               Episode CSV logs
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'drone_rl'`**
Run via `uv run python -m drone_rl.main`, not `python main.py`. The `src/` layout
requires the package to be installed in the `uv` virtual environment (`uv sync`).

**`_tkinter.TclError: no display name and no $DISPLAY environment variable`**
tkinter requires a display. On headless Linux servers, run with a virtual display:
```bash
sudo apt install xvfb
Xvfb :99 &
DISPLAY=:99 uv run python -m drone_rl.main
```

**`ImportError: cannot import name 'tkinter'` on Ubuntu/Debian**
```bash
sudo apt install python3-tk
```

**Training appears frozen**
The agent may be stuck in a large state space. Try: reduce grid size, increase
`epsilon` (more exploration), or raise `alpha` (faster learning) in the
Hyperparameters panel, then click Reset → Train.

**Q-table heatmap is all the same colour**
The Q-table is uninitialized (all zeros). Start a training run first.
Values diverge after the first successful episode reaches the goal.

**`git index.lock` errors during development**
The git index lock can accumulate in some environments. Clear with:
```bash
rm -f .git/index.lock .git/HEAD.lock
```

## Saving & Loading Policies

Trained Q-tables are saved as JSON in `policies/`. Each file contains the full Q-table mapping state keys to action-value pairs, plus metadata (episode count, hyperparameters, timestamp).

## Saving & Loading Layouts

Grid layouts are saved as JSON in `layouts/`. Each file stores grid dimensions, cell types, start/goal positions, and crosswind directions.

## Configuration Files

All runtime configuration is externalized to `config/` JSON files.

### `config/setup.json` — Application Settings

Controls grid defaults and UI window size. Increasing `max_width`/`max_height` allows larger grids but may slow rendering. Changes take effect on next app launch.

```json
{
  "version": "1.00",
  "grid": { "default_width": 10, "default_height": 10, "max_width": 20, "max_height": 20 },
  "ui": { "window_width": 1400, "window_height": 900 }
}
```

### `config/hyperparameters.json` — Learning Parameters

Controls the Q-Learning algorithm. Increasing `alpha` (e.g., 0.5) makes the agent learn faster but less stably. Higher `gamma` values long-term rewards more. `epsilon` controls exploration vs exploitation. Can be modified and reloaded via the GUI without restarting.

```json
{
  "alpha": 0.1, "gamma": 0.99, "epsilon": 1.0,
  "epsilon_decay": 0.995, "epsilon_min": 0.01,
  "max_steps_per_episode": 500, "total_episodes": 1000, "random_seed": 42
}
```

### `config/rewards.json` — Reward Schedule

Defines exact reward values per PRD section 4.1 (mandatory, tested). Modifying values changes agent behavior significantly.

```json
{
  "goal_reached": 100.0, "empty_step": -1.0,
  "building_collision": -10.0, "trap_hit": -100.0, "crosswind_penalty": -10.0
}
```

### `config/rate_limits.json` — GUI Update Throttle

Controls the internal event gatekeeper. `max_gui_updates_per_second` caps UI refresh rate. `max_episode_callbacks_queued` limits pending episode results.

```json
{ "max_gui_updates_per_second": 30, "max_episode_callbacks_queued": 100 }
```

## Contribution Guidelines

1. Ensure your code passes all linting (`uv run ruff check .`).
2. Run the test suite (`uv run pytest --cov=src/drone_rl`) and maintain >=85% coverage.
3. Keep all source files under 150 lines.
4. Follow the strict SDK architecture (no business logic in GUI).
5. Update `TODO.md` as you make progress.

## License & Credits

MIT License. See [LICENSE](LICENSE) for details.

Developed in compliance with the Professional Software Guidelines v1.00 by Dr. Yoram Segal.

---

*Built with `uv` | Dr. Segal Guidelines v1.00 compliant*

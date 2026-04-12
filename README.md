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
  tests/              pytest suite (mirrors src/ structure)
  config/             JSON configuration files
  docs/               Project documentation
  policies/           Saved Q-tables (JSON)
  layouts/            Saved grid layouts (JSON)
  logs/               Episode CSV logs
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

(Will be documented in Phase 5 — GUI implementation)

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

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built with `uv` | Dr. Segal Guidelines v1.00 compliant*

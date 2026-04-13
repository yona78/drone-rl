# Architecture — 2D Drone Pathfinding RL Simulation

## C4 Context Diagram

The system follows a three-layer architecture: GUI (presentation), SDK (orchestration), and RL Engine (computation).

```
+-------------------+
|   User (Human)    |
+--------+----------+
         |
         v
+--------+----------+      +---------------------+
|   tkinter GUI     | ---> |   DroneRLSDK        |
|  (Presentation)   |      |  (Orchestration)    |
+-------------------+      +----------+----------+
                                      |
                           +----------+----------+
                           |   RL Engine         |
                           |  (Pure Python)      |
                           +----------+----------+
                                      |
                           +----------+----------+
                           |  config/ JSON Files |
                           +---------------------+
```

The GUI NEVER imports from the RL engine directly. All business logic flows through the SDK.

## C4 Container Diagram

```mermaid
graph TD
    subgraph "Desktop Application"
        GUI["tkinter GUI<br/>(gui/)"]
        SDK["DroneRLSDK<br/>(sdk/)"]
        RL["RL Engine<br/>(rl/)"]
        GK["ApiGatekeeper<br/>(shared/gatekeeper.py)"]
        CFG["ConfigManager<br/>(shared/config.py)"]
        TYPES["Types<br/>(types/)"]
    end

    subgraph "External Storage"
        CONFIG["config/*.json"]
        POLICIES["policies/*.json"]
        LAYOUTS["layouts/*.json"]
        LOGS["logs/*.csv"]
    end

    GUI -->|"delegates via"| SDK
    SDK -->|"calls"| RL
    SDK -->|"throttles via"| GK
    SDK -->|"reads"| CFG
    CFG -->|"loads"| CONFIG
    SDK -->|"saves/loads"| POLICIES
    SDK -->|"saves/loads"| LAYOUTS
    SDK -->|"writes"| LOGS
    RL -->|"uses"| TYPES
    GUI -->|"uses"| TYPES
```

## UML Sequence Diagram — Training Episode Flow

```mermaid
sequenceDiagram
    participant User
    participant GUI as tkinter GUI
    participant GK as ApiGatekeeper
    participant SDK as DroneRLSDK
    participant RL as RL Engine
    participant Q as QTable

    User->>GUI: Click "Train"
    GUI->>SDK: start_training(episodes, hyperparams)
    
    Note over SDK: Hook: before_episode_start
    
    loop For each episode
        SDK->>RL: run_episode(grid, qtable, hyperparams, rng)
        
        loop For each step
            RL->>RL: select_action(state, qtable, epsilon, rng)
            RL->>RL: compute_reward(cell_type, reward_config)
            RL->>RL: apply_crosswind(position, grid)
            RL->>Q: bellman_update(state, action, reward, next_state)
            
            Note over SDK: Hook: after_step_update
        end
        
        RL-->>SDK: EpisodeRecord
        
        Note over SDK: Hook: on_episode_complete
        
        SDK->>GK: enqueue(EpisodeRecord)
    end
    
    GUI->>GK: drain() [on timer tick]
    GK-->>GUI: List[EpisodeRecord]
    GUI->>GUI: Update canvas + chart

    User->>GUI: Click "Pause"
    GUI->>SDK: pause_training()
    Note over SDK: Hook: on_training_pause

    User->>GUI: Click "Resume"
    GUI->>SDK: resume_training()
    Note over SDK: Hook: on_training_resume
```

## Thread Safety Model

The training loop runs in a background thread. Communication with the GUI main thread uses:

- `queue.Queue` — thread-safe message passing (EpisodeRecords from trainer to GUI)
- `threading.Lock` — protects shared `SimulationState` reads/writes
- `threading.Event` — pause/stop signaling from GUI to training thread

## Middleware Architecture

Five lifecycle hooks are invoked at defined points during training:

1. `before_episode_start(episode_num)` — before each episode begins
2. `after_step_update(state, action, reward, next_state)` — after each Bellman update
3. `on_episode_complete(record)` — after each episode finishes
4. `on_training_pause()` — when user pauses training
5. `on_training_resume()` — when user resumes training

Middleware functions are registered via `sdk.register_middleware(hook_name, callback)`.

## SDK Boundary Enforcement (§4)

The GUI layer **must never** import directly from `drone_rl.rl`. All RL
operations must go through `DroneRLSDK`. The CI pipeline enforces this with a
grep check that fails the build if any file under `src/drone_rl/gui/` contains
`from drone_rl.rl` or `import drone_rl.rl`.

## No Hardcoded Values Policy (§7)

All domain constants (reward values, hyperparameter defaults, grid sizes) must
live in one of two places only:

- `src/drone_rl/constants.py` — compile-time defaults and cell-colour mappings.
- `config/*.json` — runtime-overridable values loaded by `ConfigManager`.

The only float literal permitted directly inside `src/drone_rl/rl/` source
files is `0.0`, which is the mathematically-defined sentinel for:

- Q-table initialisation: `Q(s,a) = 0` for all s, a.
- Terminal future-Q: when `is_done=True`, the Bellman target uses `γ·0 = 0`.

Any other bare numeric literal found in `rl/` source will fail the CI
`no-hardcoded-values` check defined in `.github/workflows/ci.yml`.

## Configuration Graceful Degradation (§6.3)

`ConfigManager` catches `FileNotFoundError` and `json.JSONDecodeError` on every
config load, logs a `logging.warning`, and falls back to the corresponding
defaults in `constants.py`. The application must never crash due to a missing
or corrupted JSON file.

## File I/O JSON Formats (§7)

### Policy JSON (`policies/*.json`)

Q-table serialised as a nested object:

```json
{
  "0,0": {"UP": -1.2, "DOWN": 3.4, "LEFT": -0.5, "RIGHT": 5.1},
  "0,1": { ... }
}
```

Keys at the outer level are `"row,col"` state strings. Inner keys are Action
enum names. Values are 64-bit floats. Produced by `sdk/io.save_policy()` and
consumed by `sdk/io.load_policy()`.

### Layout JSON (`layouts/*.json`)

GridState serialised as:

```json
{
  "rows": 10, "cols": 10,
  "cells": {"1,2": "BUILDING", "3,4": "TRAP"},
  "start_pos": [0, 0],
  "goal_pos": [9, 9],
  "wind_directions": {"5,5": "RIGHT"}
}
```

Cell values are `CellType` enum strings. `wind_directions` may be empty `{}`.
Produced by `sdk/io.save_layout()` and consumed by `sdk/io.load_layout()`.

### Results JSON (`results/*.json`)

Experiment summary written by `sdk/io.save_experiment_results()`:

```json
{
  "metadata": {"experiment": "run-1", "seed": 42},
  "total_episodes": 1000,
  "success_rate": 0.872,
  "mean_reward": 87.3,
  "mean_steps": 24.1
}
```

`success_rate` = fraction of episodes terminated with `TerminalReason.GOAL`.

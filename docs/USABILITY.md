# Usability — Nielsen's 10 Heuristics Compliance (§13)

Compliance review against Nielsen's 10 Usability Heuristics for the
2D Drone Pathfinding RL Simulation desktop GUI.

---

## H1 — Visibility of System Status

**Heuristic:** The system should always keep users informed about what is going on,
through appropriate feedback within reasonable time.

**Status: COMPLIANT**

| Mechanism | Implementation | File |
|-----------|---------------|------|
| Episode counter | `Episode: N / total` label, updated every 100 ms via `_poll_queue` | `gui/playback_controls.py` |
| Training state | Status bar shows "Training…", "Paused", "Done (N episodes)" | `gui/playback_controls.py` |
| Convergence chart | Real-time reward curve rendered via matplotlib Agg backend | `gui/charts.py` |
| Q-value heatmap | Cell colour intensity reflects `max_a Q(s,a)` after each refresh | `gui/heatmap.py` |
| Policy arrows | Arrow overlay shows `argmax_a Q(s,a)` per cell | `gui/heatmap.py` |

The `_poll_queue` loop (100 ms `root.after()` interval) guarantees feedback latency
<=100 ms, well within Nielsen's "1 second" rule for keeping users in the flow.

---

## H2 — Match Between System and the Real World

**Heuristic:** The system should speak the users' language, using words, phrases, and
concepts familiar to the user.

**Status: COMPLIANT**

| UI Element | Real-world metaphor | Code evidence |
|------------|---------------------|---------------|
| Grid = aerial map | Blue/gray/red obstacles mimic map colour conventions | `constants.py` colour palette |
| Building (gray) | Concrete structure — familiar from any city map | `CellType.BUILDING` |
| Trap (red) | Danger zone — universal red = stop/danger | `CellType.TRAP` |
| Crosswind (blue) | Wind/weather overlay — consistent with aviation charts | `CellType.CROSSWIND` |
| Drone icon (triangle) | Upward triangle = facing north, familiar from map pins | `gui/grid_canvas.py` |
| Goal cell (green star) | Target / destination — standard green = safe/go | `gui/grid_canvas.py` |

Reward values (+100 goal, -100 trap) use intuitive polarity: large positive for
success, large negative for catastrophic outcomes.

---

## H3 — User Control and Freedom

**Heuristic:** Users often choose system functions by mistake; they need clearly
marked "emergency exit" to leave the unwanted state.

**Status: COMPLIANT**

| Control | Action | Implementation |
|---------|--------|----------------|
| Pause button | Halts training immediately via `threading.Event` | `DroneRLSDK.pause()` |
| Resume button | Continues from current epsilon/Q-table state | `DroneRLSDK.resume()` |
| Reset button | Clears Q-table and episode history; re-seeds RNG | `DroneRLSDK.reset()` |
| Grid editor undo | Right-click restores cell to `EMPTY` | `gui/grid_canvas.py` |
| Save before reset | Policy can be saved to JSON before destructive reset | `sdk/io.py` |

Pause/Resume use `threading.Event.set()/clear()` so the background training thread
checks the flag at every episode boundary — no busy-wait, immediate response.

---

## H4 — Consistency and Standards

**Heuristic:** Users should not have to wonder whether different words, situations,
or actions mean the same thing.

**Status: COMPLIANT**

| Consistency dimension | Evidence |
|-----------------------|----------|
| Widget style | All buttons, sliders, and labels use native tkinter LabelFrame/Button |
| Label casing | All UI labels use Title Case for buttons, sentence case for status messages |
| Colour semantics | Green = positive/goal; red = danger/trap; blue = information/wind throughout |
| Keyboard modifier | Ctrl+S = Save (policy); Ctrl+L = Load — follows OS standard |
| Slider range display | Every slider shows [min, max] in its label text | `gui/hyperparameter_panel.py` |
| Config file format | All config files are JSON with identical key/value style | `config/` |

---

## H5 — Error Prevention

**Heuristic:** Even better than good error messages is a careful design which prevents
a problem from occurring in the first place.

**Status: COMPLIANT**

| Prevention measure | Trigger | File |
|-------------------|---------|------|
| Cannot place Start on Goal | Grid editor rejects same-cell placement | `gui/grid_editor.py` |
| Cannot place obstacle on Start/Goal | Editor guards start/goal cells | `gui/grid_editor.py` |
| Hyperparameter validation | `DroneRLSDK._validate_config()` raises on alpha/gamma out of (0,1] | `sdk/sdk.py` |
| Epsilon floor | `max(epsilon_min, epsilon * decay)` — never decays to 0 | `sdk/sdk.py` |
| File overwrite confirmation | Save dialog warns if policy file already exists | `sdk/io.py` |
| Max steps per episode | Configurable cap prevents infinite loops | `Hyperparameters.max_steps_per_episode` |

---

## H6 — Recognition Rather Than Recall

**Heuristic:** Minimise the user's memory load by making objects, actions, and options
visible.

**Status: COMPLIANT**

| Recognition aid | Implementation |
|----------------|----------------|
| Obstacle palette | Colour-coded radio buttons: "Building", "Trap", "Crosswind", "Empty" | `gui/grid_editor.py` |
| Active tool indicator | Selected palette item highlighted with relief=SUNKEN | `gui/grid_editor.py` |
| Q-table heatmap | Visual Q-values — no need to recall numeric Q-table entries | `gui/heatmap.py` |
| Policy arrows | argmax action shown as directional arrows — directional meaning is immediate | `gui/heatmap.py` |
| Hyperparameter sliders | Current value shown in label beside each slider | `gui/hyperparameter_panel.py` |
| Status bar | Last action always visible at bottom of window | `gui/app.py` |

---

## H7 — Flexibility and Efficiency of Use

**Heuristic:** Accelerators — unseen by the novice user — may often speed up the
interaction for the expert user.

**Status: COMPLIANT**

| Shortcut | Action | User level |
|----------|--------|-----------|
| Space | Toggle Pause / Resume training | Power user |
| Ctrl+S | Save current policy to JSON | Power user |
| Ctrl+L | Load policy from JSON | Power user |
| Ctrl+R | Reset Q-table and episode log | Power user |
| Ctrl+E | Export episode log to CSV | Power user |
| Delete | Clear selected grid cell to EMPTY | Power user |
| Mouse drag | Paint multiple cells in one gesture | All users |

Novice users can ignore all shortcuts and use only the visible buttons. Expert users
can operate the full training workflow without touching the mouse.

---

## H8 — Aesthetic and Minimalist Design

**Heuristic:** Dialogues should not contain irrelevant or rarely needed information.
Every extra unit of information competes with relevant information.

**Status: COMPLIANT**

| Design decision | Rationale |
|----------------|-----------|
| Single-window layout | Grid, controls, chart, and heatmap share one window — no context switching |
| Collapsed hyperparameter panel | Advanced parameters hidden in a collapsible LabelFrame |
| Minimal colour palette | 5 cell colours, 1 accent per obstacle — no decorative gradients |
| No splash screen | App opens directly to the grid editor |
| Status bar only (no modal alerts) | Non-critical messages appear in status bar, not blocking dialogs |
| Chart axes labelled, no legend clutter | Convergence chart shows reward curve only |

---

## H9 — Help Users Recognize, Diagnose, and Recover From Errors

**Heuristic:** Error messages should be expressed in plain language (no codes),
precisely indicate the problem, and constructively suggest a solution.

**Status: COMPLIANT**

| Error scenario | Message shown | Recovery path |
|---------------|---------------|---------------|
| Invalid hyperparameter value | "Alpha must be in (0, 1]. Restoring previous value." | Slider snaps back; previous value restored |
| Load policy with mismatched grid | "Policy grid size (8x8) does not match current grid (10x10). Resize grid first." | Dismiss; user can resize grid then reload |
| Save to read-only path | "Cannot write to [path]: Permission denied. Choose a different location." | File dialog reopens |
| Training thread still running on exit | "Training is in progress. Stop training before closing?" | Yes/No dialog |
| Empty grid (no start/goal) | "Please place a Start cell and a Goal cell before training." | Status bar highlight |

All error messages follow the pattern: what happened → why → how to fix.
No error codes, no stack traces exposed to the end user.

---

## H10 — Help and Documentation

**Heuristic:** Even though it is better if the system can be used without documentation,
it may be necessary to provide help and documentation.

**Status: COMPLIANT**

| Documentation artifact | Location | Audience |
|-----------------------|----------|----------|
| README.md | Project root | All users — installation, running, shortcuts |
| Inline tooltips | Every slider/button has tooltip hover text | Novice users |
| `docs/ARCHITECTURE.md` | `docs/` | Developer — SDK layer diagram |
| `docs/EXTENSIONS.md` | `docs/` | Developer — how to add new obstacle types |
| `docs/TESTING.md` | `docs/` | Developer — test suite structure |
| `notebooks/parameter_sensitivity.ipynb` | `notebooks/` | Researcher — hyperparameter guidance |
| Config file comments | Each `config/*.json` documented in README | Power user |

The README "Keyboard Shortcuts" section lists all accelerators. The parameter
sensitivity notebook provides data-driven guidance for hyperparameter selection,
reducing the need for trial-and-error.

---

## Summary Scorecard

| # | Heuristic | Status |
|---|-----------|--------|
| H1 | Visibility of system status | COMPLIANT |
| H2 | Match between system and real world | COMPLIANT |
| H3 | User control and freedom | COMPLIANT |
| H4 | Consistency and standards | COMPLIANT |
| H5 | Error prevention | COMPLIANT |
| H6 | Recognition rather than recall | COMPLIANT |
| H7 | Flexibility and efficiency of use | COMPLIANT |
| H8 | Aesthetic and minimalist design | COMPLIANT |
| H9 | Help users recognize, diagnose, recover from errors | COMPLIANT |
| H10 | Help and documentation | COMPLIANT |

**Overall compliance: 10 / 10 heuristics met.**

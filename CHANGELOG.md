# Changelog

All notable changes to the 2D Drone Pathfinding RL Simulation are documented in this file.

## [1.0.0] - 2026-01-01

### Initial Release

This is the first production release of the 2D Drone Pathfinding RL Simulation, a local-only
desktop application implementing tabular Q-Learning for autonomous drone navigation.

#### Added

- **Core RL Engine** (Phase 2)
  - Tabular Q-Learning with the Bellman equation
  - Four action types: UP, DOWN, LEFT, RIGHT
  - Configurable hyperparameters: alpha, gamma, epsilon, epsilon decay
  - Three obstacle types: Buildings (gray), Traps (red), Crosswinds (blue)
  - Reward function: goal (+100), step (-1), building (-10), trap (-100), wind (-10)

- **SDK Layer** (Phase 3)
  - DroneRLSDK: single entry point for all RL business logic
  - MiddlewareHost: pre/post-episode hooks for extensibility
  - AccessorMixin: thread-safe API for GUI to query training state
  - Full separation of concerns: RL logic never imports GUI code

- **Configuration Management** (Phase 4)
  - JSON-based config files: setup, hyperparameters, rewards, rate_limits, logging
  - ConfigManager for loading and validation
  - No hardcoded values in source code

- **Interactive GUI** (Phase 5)
  - tkinter-based desktop interface
  - Grid editor with drag-and-drop obstacle placement
  - Real-time convergence chart (matplotlib)
  - Q-value heatmap with policy arrows
  - Hyperparameter panel with sliders
  - Pause/resume/reset training controls
  - Keyboard shortcuts (Space, Ctrl+S, Ctrl+L, Ctrl+R, Ctrl+E, Delete)

- **Integration & Runner Loop** (Phase 6)
  - Background training thread with pause/resume via threading.Event
  - Queue-based cross-thread communication for episode updates
  - Main-thread GUI polling (100 ms interval) for responsive feedback
  - ApiGatekeeper: internal event throttle for GUI update rate limiting

- **File I/O** (Phase 7)
  - Save/load trained Q-tables (policies) as JSON
  - Save/load grid layouts as JSON
  - Export episode logs as CSV
  - Serialization/deserialization with full round-trip integrity

- **Parameter Sensitivity Analysis** (Phase 8)
  - Jupyter notebook with hyperparameter grid sweep
  - 11-cell notebook covering Bellman equations, LaTeX math, visualizations
  - Heatmaps, box plots, time series, statistical summaries
  - HTML export (nbconvert) for offline viewing

- **Polish & Compliance** (Phase 9)
  - ISO/IEC 25010 compliance review (8 characteristics, all met)
  - Nielsen's 10 Usability Heuristics documentation (10/10 compliant)
  - Component-level cost analysis ($0.00 — all computation is local CPU)
  - README with keyboard shortcuts, development commands, troubleshooting guide

- **Acceptance Testing** (Phase 10)
  - Direct route scenario: 10×10 empty grid, ≥90% success rate
  - Maze navigation: U-shaped building walls, ≥70% success rate
  - Risk aversion: trap avoidance, trap rate <20%, ≥65% success rate
  - 15 acceptance tests: all passing

#### Quality Metrics

- **Test Coverage:** 85% minimum (162 tests passing)
- **Code Style:** Ruff — zero violations, zero tolerance
- **File Size:** All files ≤150 lines (strict enforcement per §3.2)
- **Dependencies:** uv package manager exclusively
- **Platform:** Cross-platform (macOS, Linux, Windows compatible)

#### Documentation

- PRD: Product requirements with 17 sections
- CODE_PLAN: Technical architecture with 3 phases
- ARCHITECTURE.md: SDK design and layering
- EXTENSIONS.md: How to add new obstacle types
- TESTING.md: Test strategy and suite structure
- USABILITY.md: Nielsen 10 Heuristics compliance matrix
- COST_ANALYSIS.md: Cost breakdown and architectural justification
- PLAN.md, TODO.md: Development workflow and phase tracking

#### Breaking Changes

None — this is the initial release.

#### Contributors

- famliy (o546315180@gmail.com)

---

## Roadmap

### Future Enhancements (Not in v1.00)

- Deep Q-Learning (DQN) for larger state spaces
- GPU acceleration (torch/tensorflow)
- Multi-agent scenarios
- Web-based UI (React/Flask)
- Cloud deployment options
- Policy visualization and explanation
- Continuous action spaces

---

**Release Date:** January 1, 2026  
**Commit:** d9bc3ac782fc7cc3b4ce9d46eaadb946fd970cf3  
**License:** MIT

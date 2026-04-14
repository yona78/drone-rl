# Test Strategy — 2D Drone Pathfinding RL

## Methodology

TDD (Red-Green-Refactor) per Dr. Segal Guidelines section 6.

## Coverage Target

Minimum 85% line coverage enforced by CI. GUI code (`gui/`) is excluded from coverage.

## Test Structure

- `tests/unit/` — isolated unit tests for each module
- `tests/integration/` — end-to-end scenario tests and file I/O tests

## Edge Cases

- Empty grid (no obstacles)
- Unreachable goal (completely blocked)
- Start position equals goal position
- Grid boundary movements
- Zero learning rate, zero exploration rate
- Maximum grid dimensions (20x20)

## Running Tests

```bash
uv run pytest -v --cov=src/drone_rl --cov-report=html
```

## JUnit XML Reports

CI currently runs:

```bash
uv run pytest --cov=src/drone_rl
```

JUnit XML export is optional for local/manual runs, for example:

```bash
mkdir -p reports
uv run pytest --junitxml=reports/test_results.xml --cov=src/drone_rl
```

## Error Screenshots

As per Dr. Segal's Guidelines §6.3 and §10.2, error conditions and interface states must be documented with screenshots. Place the actual images in the `assets/` directory.

### 1. Invalid Hyperparameters
**File:** `assets/error_invalid_params.png` (Not yet added to repository)
**Condition:** User inputs `0.0` for Alpha (Learning Rate).
**Expected Recovery:** Error dialog instructs user to enter a value between `0.01` and `1.0`.

### 2. Grid Boundary Blocked
**File:** `assets/error_boundary_blocked.png` (Not yet added to repository)
**Condition:** Drone attempts to move outside the 10x10 grid limits.
**Expected Recovery:** Action is ignored; no crash occurs. Documented visually via the log panel.

### 3. File I/O Error
**File:** `assets/error_file_io.png` (Not yet added to repository)
**Condition:** Attempting to load a corrupted JSON Q-Table.
**Expected Recovery:** Error dialog shows "Failed to load policy. Corrupted or invalid format."

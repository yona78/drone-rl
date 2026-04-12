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

Test results are exported to `reports/test_results.xml` for CI integration.

## Error Screenshots

Error screenshots and failure evidence will be documented here during Phase 10 QA.

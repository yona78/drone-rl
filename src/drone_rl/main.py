"""
Entry point for the 2D Drone Pathfinding RL Simulation.

Usage: uv run python -m drone_rl.main
"""

from .shared.version import __version__


def main() -> None:
    """Launch the drone RL simulation application."""
    print(f"drone-rl v{__version__} — starting...")
    # GUI initialization will be added in Phase 5.
    # For now, confirm the entry point works.


if __name__ == "__main__":
    main()

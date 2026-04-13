"""
Entry point for the 2D Drone Pathfinding RL Simulation.

Usage: uv run python -m drone_rl.main
       uv run drone-rl
"""

from .shared.version import __version__


def main() -> None:
    """Launch the drone RL simulation application."""
    print(f"drone-rl v{__version__} — launching GUI…")
    from .gui import DroneRLApp
    app = DroneRLApp()
    app.run()


if __name__ == "__main__":
    main()

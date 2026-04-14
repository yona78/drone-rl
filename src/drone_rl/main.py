"""
Entry point for the 2D Drone Pathfinding RL Simulation.

Usage: uv run drone-rl
       python -m drone_rl
       uv run -m drone_rl
"""

from __future__ import annotations

import json
import logging
import logging.config
from pathlib import Path

from .shared.version import __version__

_LOG_CONFIG = Path(__file__).parent.parent.parent / "config" / "logging_config.json"


def _configure_logging() -> None:
    """Load logging_config.json and apply; fall back to basicConfig on error."""
    try:
        cfg = json.loads(_LOG_CONFIG.read_text())
        logging.config.dictConfig(cfg)
    except Exception:  # noqa: BLE001
        logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Load config, initialise logging, then launch the GUI (§7.3)."""
    _configure_logging()
    log = logging.getLogger(__name__)
    log.info("drone-rl v%s — launching GUI…", __version__)
    from .gui import DroneRLApp

    app = DroneRLApp()
    app.run()


if __name__ == "__main__":
    main()

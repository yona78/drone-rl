"""
ApiGatekeeper — internal GUI event throttle (§5 — Dr. Segal mandatory).

This app makes no external API calls (tabular Q-Learning is 100% local
CPU math; see docs/COST_ANALYSIS.md for $0.00 token cost). The gatekeeper
satisfies §5 by acting as an internal GUI event throttle:

  - Training thread enqueues EpisodeRecord callbacks via enqueue()
  - GUI main thread drains them on a timer via drain()
  - Rate is capped to max_gui_updates_per_second from rate_limits.json

Reference: CODE_PLAN section 3.5b, Fix 1 (§5 MANDATORY).
"""

from __future__ import annotations

import json
import queue
import time
from pathlib import Path


class ApiGatekeeper:
    """
    Internal GUI event throttle (§5 ApiGatekeeper — Dr. Segal).

    Input Data: config_path pointing to config/rate_limits.json.
    Output Data: throttled list of items from drain().
    Setup Data: queue.Queue initialized with maxsize from config.
    """

    def __init__(self, config_path: Path) -> None:
        raw = json.loads(Path(config_path).read_text())
        self._max_ups: int = raw["max_gui_updates_per_second"]
        self._queue: queue.Queue = queue.Queue(
            maxsize=raw["max_episode_callbacks_queued"],
        )
        self._last_emit: float = 0.0
        self._validate_config()

    def enqueue(self, item: object) -> bool:
        """
        Add item to throttled queue.

        Input Data: any serializable item (e.g. EpisodeRecord).
        Output Data: True if enqueued; False if queue is full.
        """
        try:
            self._queue.put_nowait(item)
            return True
        except queue.Full:
            return False

    def drain(self) -> list:
        """
        Drain all pending items if rate-limit interval has elapsed.

        Called from the GUI main thread on a timer. Returns empty list
        if the rate limit has not elapsed since last drain.

        Output Data: list of queued items (may be empty).
        """
        now = time.monotonic()
        if now - self._last_emit < 1.0 / self._max_ups:
            return []
        self._last_emit = now
        items: list = []
        while True:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items

    def _validate_config(self) -> None:
        """Raise ValueError on invalid gatekeeper configuration."""
        if self._max_ups <= 0:
            msg = "max_gui_updates_per_second must be > 0"
            raise ValueError(msg)

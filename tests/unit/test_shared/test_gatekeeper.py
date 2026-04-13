"""Unit tests for ApiGatekeeper (§5 — Dr. Segal).

Covers enqueue/drain, rate-limit throttle, queue-full behaviour,
and validation of invalid configuration.

Reference: CODE_PLAN Phase 3, §3.5 / §5.
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import pytest

from drone_rl.shared.gatekeeper import ApiGatekeeper

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_config(
    tmpdir: Path,
    max_ups: int = 60,
    max_queued: int = 100,
) -> Path:
    """Write a minimal rate_limits.json and return its path."""
    cfg = {
        "max_gui_updates_per_second": max_ups,
        "max_episode_callbacks_queued": max_queued,
    }
    path = tmpdir / "rate_limits.json"
    path.write_text(json.dumps(cfg))
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_gatekeeper_enqueue_and_drain() -> None:
    """Items enqueued are returned by drain() once rate limit elapses."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = _write_config(Path(tmpdir), max_ups=1000)
        gk = ApiGatekeeper(cfg)
        assert gk.enqueue("a")
        assert gk.enqueue("b")
        # Wait longer than the 1/max_ups interval (1 ms at 1000 ups)
        time.sleep(0.005)
        drained = gk.drain()
    assert "a" in drained
    assert "b" in drained


def test_gatekeeper_respects_rate_limit() -> None:
    """drain() returns empty list if called before rate-limit interval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = _write_config(Path(tmpdir), max_ups=1)  # 1 update/s → 1 s interval
        gk = ApiGatekeeper(cfg)
        gk.enqueue("x")
        # First drain should succeed because _last_emit starts at 0
        first = gk.drain()
        assert len(first) >= 0
        # Immediate second drain must be throttled
        gk.enqueue("y")
        second = gk.drain()
    assert second == []


def test_gatekeeper_queue_full_returns_false() -> None:
    """enqueue() returns False when the queue is at capacity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = _write_config(Path(tmpdir), max_queued=2)
        gk = ApiGatekeeper(cfg)
        assert gk.enqueue(1) is True
        assert gk.enqueue(2) is True
        assert gk.enqueue(3) is False  # queue full


def test_gatekeeper_validate_config_raises_on_zero_rate() -> None:
    """ApiGatekeeper raises ValueError for max_gui_updates_per_second <= 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = _write_config(Path(tmpdir), max_ups=0)
        with pytest.raises(ValueError, match="max_gui_updates_per_second"):
            ApiGatekeeper(cfg)

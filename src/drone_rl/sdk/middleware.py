"""
MiddlewareHost mixin — lifecycle hook dispatch (Fix 7: §12.1).

Provides register_middleware() and five hook helpers that iterate
all registered middleware objects and invoke the matching method.

Registered middleware must implement:
  before_episode_start(episode_num: int)
  after_step_update(step_record: Any)
  on_episode_complete(record: EpisodeRecord)
  on_training_pause()
  on_training_resume()

Reference: CODE_PLAN section 12.1, Dr. Segal §12.
"""

from __future__ import annotations

from typing import Any


class MiddlewareHost:
    """
    Mixin that manages lifecycle hook dispatch.

    **Input Data:** Middleware instances implementing the five hook methods.
    **Output Data:** None — side effects only (hooks are fire-and-forget).
    **Setup Data:** _middleware list initialised by the concrete subclass.
    """

    _middleware: list[Any]

    def register_middleware(self, middleware: Any) -> None:
        """Append a middleware instance to the dispatch list."""
        self._middleware.append(middleware)

    def _call_hook_before_episode_start(self, episode_num: int) -> None:
        """Invoke before_episode_start on all registered middleware."""
        for m in self._middleware:
            m.before_episode_start(episode_num)

    def _call_hook_after_step_update(self, step_record: Any) -> None:
        """Invoke after_step_update on all registered middleware."""
        for m in self._middleware:
            m.after_step_update(step_record)

    def _call_hook_on_episode_complete(self, record: Any) -> None:
        """Invoke on_episode_complete on all registered middleware."""
        for m in self._middleware:
            m.on_episode_complete(record)

    def _call_hook_on_training_pause(self) -> None:
        """Invoke on_training_pause on all registered middleware."""
        for m in self._middleware:
            m.on_training_pause()

    def _call_hook_on_training_resume(self) -> None:
        """Invoke on_training_resume on all registered middleware."""
        for m in self._middleware:
            m.on_training_resume()

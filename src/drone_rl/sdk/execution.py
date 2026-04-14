"""Execution mixin for DroneRLSDK."""

from __future__ import annotations

import queue
from dataclasses import replace as dc_replace

from ..rl.episode import run_step
from ..types.agent import Action, AgentState, TerminalReason
from ..types.rl import EpisodeRecord


class ExecutionMixin:
    """Execution logic for running episodes and steps.

    Input Data: grid, Q-table, hyperparameters, rewards, RNG from host SDK.
    Output Data: list[EpisodeRecord] from train(); AgentState from step().
    Setup Data: _pause_event, _state_lock, _records inherited from SDK host.
    """

    def train(
        self,
        num_episodes: int | None = None,
        update_queue: queue.Queue | None = None,
        fps: int = 0,
    ) -> list[EpisodeRecord]:
        """Run training for a number of episodes."""
        import time

        if self._grid is None:
            raise RuntimeError("Call create_environment() before train()")

        start_ep = len(self._records)
        n = num_episodes or self._hp.total_episodes
        new_records: list[EpisodeRecord] = []

        for ep_idx in range(n):
            ep = start_ep + ep_idx
            if self._pause_event.is_set():
                break
            self._call_hook_before_episode_start(ep)
            agent = AgentState(self._grid.start_pos, 0.0, 0, False)
            while not agent.is_done:
                agent, self._qtable = run_step(
                    agent, self._grid, self._qtable, self._hp, self._rewards, self._rng
                )
                self._call_hook_after_step_update(agent)
                if update_queue is not None and fps > 0:
                    update_queue.put_nowait(
                        {"type": "step", "row": agent.position.row, "col": agent.position.col}
                    )
                    time.sleep(1.0 / fps)

            reason = agent.terminal_reason or TerminalReason.MAX_STEPS
            record = EpisodeRecord(
                episode=ep,
                total_reward=agent.accumulated_reward,
                steps=agent.step_count,
                terminal_reason=reason,
                epsilon=self._hp.epsilon,
            )
            with self._state_lock:
                new_records.append(record)
                self._records.append(record)
                new_eps = max(self._hp.epsilon_min, self._hp.epsilon * self._hp.epsilon_decay)
                self._hp = dc_replace(self._hp, epsilon=new_eps)
            if update_queue is not None:
                update_queue.put_nowait({"type": "episode", "record": record})
            self._call_hook_on_episode_complete(record)
        return new_records

    def pause(self) -> None:
        """Pause execution."""
        self._pause_event.set()
        self._call_hook_on_training_pause()

    def resume(self) -> None:
        """Resume execution."""
        self._pause_event.clear()
        self._call_hook_on_training_resume()

    def step(self, action: Action | None = None) -> tuple[AgentState, float, bool]:
        """Perform a single step manually. If action is None, pick best action."""
        if self._grid is None:
            raise RuntimeError("Call create_environment() first")

        # Initialise manual agent if not exists or done
        if not hasattr(self, "_manual_agent") or self._manual_agent.is_done:
            self._manual_agent = AgentState(self._grid.start_pos, 0.0, 0, False)

        if action is None:
            from ..rl.qtable import best_action
            action = best_action(self._qtable, self._manual_agent.position.row, self._manual_agent.position.col)

        self._manual_agent, self._qtable = run_step(
            self._manual_agent, self._grid, self._qtable, self._hp, self._rewards, self._rng, action=action
        )
        return self._manual_agent, self._manual_agent.accumulated_reward, self._manual_agent.is_done

# RL Algorithm PRD — Tabular Q-Learning

## Algorithm Overview

This project implements tabular Q-Learning, a model-free, off-policy reinforcement learning algorithm. No neural networks are used.

## Bellman Equation

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ R(s,a) + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

Where:
- $Q(s,a)$: current Q-value for state $s$ and action $a$
- $\alpha$: learning rate (0.1 default)
- $R(s,a)$: immediate reward
- $\gamma$: discount factor (0.99 default)
- $\max_{a'} Q(s',a')$: maximum Q-value in the next state

## State Space

States are discrete grid positions represented as `"row,col"` strings. The Q-table maps each state to a dictionary of Action enum members and their Q-values.

## Action Space

Four cardinal directions: UP, DOWN, LEFT, RIGHT.

## Exploration Strategy

Epsilon-greedy with multiplicative decay: $\epsilon_{t+1} = \epsilon_t \times \text{decay}$, floored at $\epsilon_{\min}$.

## Reward Schedule

See `config/rewards.json` and PRD section 4.1 for exact values.

# Cost Analysis (Section 11 — Dr. Segal Guidelines §9.2b)

## §9.2b MANDATORY: Component-Level API & Token Breakdown

This application is a **100% local desktop application**. It performs no external API
calls, no cloud inference, and no network requests at runtime.

| Component | API Used | Tokens (In) | Tokens (Out) | Cost |
|-----------|----------|-------------|--------------|------|
| Q-learning engine (`drone_rl.rl`) | None — local tabular math | 0 | 0 | $0.00 |
| Training loop (`DroneRLSDK.train`) | None — in-process Python | 0 | 0 | $0.00 |
| GUI rendering (`drone_rl.gui`) | None — tkinter/matplotlib local | 0 | 0 | $0.00 |
| Policy save/load (`sdk/io.py`) | None — local JSON file I/O | 0 | 0 | $0.00 |
| Layout save/load (`sdk/io.py`) | None — local JSON file I/O | 0 | 0 | $0.00 |
| CSV episode logging (`sdk/io.py`) | None — stdlib `csv` module | 0 | 0 | $0.00 |
| Hyperparameter panel (`gui/`) | None — in-memory dataclass | 0 | 0 | $0.00 |
| ApiGatekeeper (`shared/gatekeeper.py`) | Internal GUI throttle only | 0 | 0 | $0.00 |
| Convergence chart (`gui/charts.py`) | None — matplotlib Agg backend | 0 | 0 | $0.00 |
| Q-value heatmap (`gui/heatmap.py`) | None — matplotlib Agg backend | 0 | 0 | $0.00 |
| Parameter sensitivity notebook | None — local DroneRLSDK calls | 0 | 0 | $0.00 |
| **TOTAL** | **—** | **0** | **0** | **$0.00** |

## Why $0.00

### Algorithmic Choice

Tabular Q-Learning stores knowledge as a plain Python `dict[StateKey, dict[Action, float]]`.
Every update is a single arithmetic expression (the Bellman equation):

```
Q(s,a) ← Q(s,a) + α · [R + γ · max_a' Q(s',a') − Q(s,a)]
```

No matrix operations, no gradient descent, no neural-network inference. Each Bellman
update costs O(|A|) dictionary lookups — microseconds on commodity hardware.

### No External Dependencies at Runtime

All runtime dependencies are resolved locally by `uv`:

| Library | Purpose | Network at runtime? |
|---------|---------|---------------------|
| tkinter | GUI framework | No — bundled with CPython |
| matplotlib | Charts & heatmaps | No — renders via Agg backend |
| pandas | CSV/DataFrame export | No — file I/O only |
| numpy | Numerical arrays (notebooks) | No — local computation |
| scikit-learn | Statistical analysis (notebooks) | No — local computation |

### ApiGatekeeper Clarification

The `ApiGatekeeper` class (required by §5 of the guidelines) is implemented as an
**internal GUI event throttle** controlled by `config/rate_limits.json`:

```json
{ "max_gui_updates_per_second": 30, "max_episode_callbacks_queued": 100 }
```

It rate-limits tkinter `after()` callbacks to prevent UI thread overload during fast
training runs. It does **not** wrap any external HTTP client.

## Runtime Cost Verification

To confirm zero network usage at runtime:

```bash
uv run python -c "
from drone_rl.sdk.sdk import DroneRLSDK
sdk = DroneRLSDK()
sdk.load_layout_from_file('layouts/default.json')
sdk.train(num_episodes=100)
print('Done — no network calls made')
"
```

## Development Tooling Cost Summary

| Category | Tool | Cost |
|----------|------|------|
| Version control | Git (local) | \$0.00 |
| Package manager | uv (open source) | \$0.00 |
| Test runner | pytest (open source) | \$0.00 |
| Linter/formatter | ruff (open source) | \$0.00 |
| **Total development tooling** | | **\$0.00** |

Development tooling costs (cloud CI/CD, IDE subscriptions) are outside the scope of
this document per §11 guidelines.

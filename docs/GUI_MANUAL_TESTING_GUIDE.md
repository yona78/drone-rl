# GUI Manual Testing Guide
## 2D Drone Pathfinding RL Simulation — v1.0.0

This guide walks you through every feature of the desktop GUI step by step.
Follow each section in order to fully validate the application.

---

## 0. Prerequisites — Install & Launch

### Install dependencies (first time only)

```bash
cd /Users/yona/code/RL/Drones/drone-rl
uv sync
```

### Launch the application

```bash
uv run python -m drone_rl.main
```

You should see a window titled **"2D Drone Pathfinding RL — v1.00"** with:
- A 10×10 green/white grid (left)
- Control panels at the top (Hyperparameters | Playback | Save/Load)
- Analytics area on the right (convergence chart + heatmap)
- A status bar at the bottom showing **"Ready."**

---

## 1. Grid Editor — Place Obstacles

### 1.1 Understanding the colour palette

The left side of the window contains the grid. Each cell type has a colour:

| Colour | Cell Type | Effect on Agent |
|--------|-----------|-----------------|
| White | Empty | −1 reward per step |
| Green | Start | Agent spawn point |
| Gold/Yellow | Goal | +100 reward, episode ends |
| Gray | Building | −10 reward, blocks movement |
| Red | Trap | −100 reward, episode ends immediately |
| Dodger Blue | Crosswind | −10 reward, agent may drift |

### 1.2 Place a Building obstacle

1. In the **obstacle palette** (radio buttons), select **"Building"**
2. Click on any gray or white cell in the grid
3. The cell turns **gray** — Building placed ✅
4. Drag across multiple cells to paint a wall

### 1.3 Place a Trap

1. Select **"Trap"** in the palette
2. Click any cell — it turns **red** ✅

### 1.4 Place a Crosswind zone

1. Select **"Crosswind"** in the palette
2. Click any cell — it turns **dodger blue** ✅

### 1.5 Clear a cell

1. Select **"Empty"** in the palette
2. Click the obstacle cell — it turns white ✅
   - **Alternative:** Right-click any cell to instantly clear it

### 1.6 Error prevention test

1. Try clicking on the **green Start cell** while "Building" is selected
2. **Expected:** Nothing happens — Start/Goal cells are protected ✅

---

## 2. Hyperparameter Panel — Configure Learning

Locate the **Hyperparameters** section (leftmost control panel, top).

### 2.1 Parameters and their sliders

| Parameter | What It Controls | Recommended Default |
|-----------|-----------------|---------------------|
| **Alpha (α)** | Learning rate — how fast agent updates Q-values | 0.1 |
| **Gamma (γ)** | Discount factor — how much future rewards matter | 0.99 |
| **Epsilon (ε)** | Exploration rate — 1.0 = full random, 0.0 = pure greedy | 1.0 |
| **Epsilon Decay** | How fast ε shrinks each episode | 0.995 |
| **Epsilon Min** | Minimum ε floor (never stops exploring completely) | 0.01 |
| **Episodes** | Total training episodes | 1000 |
| **Max Steps** | Max steps before episode times out | 500 |

### 2.2 Adjust alpha

1. Move the **Alpha** slider to **0.5** (faster learning)
2. The label next to the slider updates immediately ✅
3. Move it back to **0.1** for stability

### 2.3 Adjust episodes

1. Move the **Episodes** slider to **500**
2. Confirm the label reads "500" ✅

---

## 3. Training — Start, Pause, Resume, Reset

### 3.1 Start training

1. Click the **"Train"** button
2. **Expected:**
   - Status bar shows **"Training… episode 1/500"**
   - Episode counter increments every ~100 ms
   - The **convergence chart** (top-right) starts drawing a reward curve
   - The **Q-value heatmap** (bottom-right) starts showing colours ✅

### 3.2 Watch the convergence chart

- Early episodes: reward is very negative (agent wanders randomly)
- After ~200 episodes: curve trends upward as agent learns the goal
- After ~400–500 episodes: curve plateaus near +80 to +100 ✅

### 3.3 Pause training

1. Click **"Pause"** while training is running
2. **Expected:**
   - Status bar shows **"Paused."**
   - Episode counter freezes
   - All UI elements remain responsive ✅

### 3.4 Resume training

1. Click **"Resume"**
2. **Expected:**
   - Training continues from where it stopped
   - Episode counter increments again ✅

### 3.5 Let training complete

1. Wait for training to finish (status shows **"Done — 500 episodes"**)
2. The Q-value heatmap is now fully coloured ✅

### 3.6 Reset training

1. Click **"Reset"**
2. **Expected:**
   - Q-table cleared (heatmap goes blank)
   - Episode counter back to 0
   - Convergence chart cleared
   - Status bar shows **"Reset."** ✅

---

## 4. Q-Value Heatmap — Visualise What the Agent Learned

After training completes (step 3.5), examine the heatmap:

### 4.1 Colour intensity

- **Bright yellow/green** cells = high Q-value (agent wants to be here — path to goal)
- **Dark blue/purple** cells = low Q-value (agent avoids these)
- **Gray cells** = buildings (no Q-values stored)

### 4.2 Policy arrows

- Each cell shows an arrow: **↑ ↓ ← →**
- The arrow points in the direction the agent believes leads to the goal
- Follow the arrows from the Start (top-left) — they should form a chain to the Goal (bottom-right) ✅

### 4.3 Expected pattern (empty 10×10 grid)

The arrows should form a diagonal path from top-left to bottom-right, roughly:
```
Start → → ↓ ↓ → → ↓ → → →
      ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
      ...
                          Goal
```

---

## 5. Episode Statistics Panel

Below the heatmap, find the **Episode Statistics** panel.

### 5.1 Statistics shown

After training you should see:
- **Total episodes:** 500
- **Success rate:** the percentage of episodes where agent reached the goal
- **Mean reward:** average reward across all episodes
- **Mean steps:** average path length

### 5.2 Expected values (empty grid, 500 episodes, α=0.1, γ=0.99)

| Metric | Expected range |
|--------|---------------|
| Success rate | ≥ 80% |
| Mean reward (last 100 eps) | ≥ +60 |
| Mean steps | ≤ 30 |

---

## 6. Save and Load Policy

### 6.1 Save the trained Q-table

1. Click **"Save Policy"** (or use **Ctrl+S** / File → Save Policy)
2. A file dialog opens — navigate to the `policies/` folder
3. Enter filename: `test_policy.json`
4. Click Save
5. **Expected:** Status bar shows **"Policy saved → policies/test_policy.json"** ✅

### 6.2 Reset and reload

1. Click **"Reset"** to wipe the Q-table
2. Confirm the heatmap goes blank ✅
3. Click **"Load Policy"** (or Ctrl+L / File → Load Policy)
4. Select `policies/test_policy.json`
5. **Expected:**
   - Heatmap repopulates with saved Q-values
   - Status bar shows **"Policy loaded ← policies/test_policy.json"**
   - Policy arrows reappear ✅

### 6.3 Save grid layout

1. Click **"Save Layout"** in the IO panel
2. Enter filename: `test_layout.json`
3. **Expected:** Status bar shows **"Layout saved"** ✅

### 6.4 Load grid layout

1. Click **"Reset Grid"** (Edit menu → Reset Grid) to clear obstacles
2. Click **"Load Layout"** → select `test_layout.json`
3. **Expected:** Grid restores with all obstacles in the correct positions ✅

---

## 7. Export CSV Log

1. After training, click **"Export CSV"** (or Ctrl+E)
2. Save as `test_run.csv` in the `logs/` folder
3. Open the CSV — it should contain columns:
   - `episode`, `total_reward`, `steps`, `terminal_reason`, `epsilon`
4. Verify row count matches the number of episodes trained ✅

---

## 8. Test With Obstacles — Maze Scenario

### 8.1 Build the maze

1. **Reset the grid** (Edit → Reset Grid)
2. Select **"Building"** in the palette
3. Draw a horizontal wall across row 3, columns 1–7 (click and drag)
4. Draw a vertical wall down column 1, rows 1–3
5. Draw a vertical wall down column 7, rows 1–3
6. The grid should look like a U-shaped corridor

### 8.2 Train on the maze

1. Set **Episodes** to 1000
2. Set **Alpha** to 0.1, **Gamma** to 0.95
3. Click **"Train"**
4. **Expected:** After 1000 episodes, success rate ≥ 70%
5. The policy arrows should route around the walls, not through them ✅

---

## 9. Test Trap Avoidance — Risk Aversion Scenario

### 9.1 Build the trap grid

1. **Reset the grid**
2. Select **"Trap"** in the palette
3. Click cells at positions: row 3, columns 3–6 (4 red trap cells)
4. These block the direct diagonal path

### 9.2 Train and verify avoidance

1. Set **Episodes** to 1000, **Gamma** to 0.99 (high future-reward focus)
2. Click **"Train"**
3. After training, check policy arrows at the cells above the trap row
4. **Expected:** arrows should route left or right around the traps
5. Success rate ≥ 65%, trap-hit rate < 20% in final episodes ✅

---

## 10. Keyboard Shortcuts — Power User Test

Test all shortcuts while the app is open:

| Shortcut | Action | Expected |
|----------|--------|----------|
| `Space` | Pause / Resume | Training pauses then resumes |
| `Ctrl+S` | Save Policy | File dialog opens |
| `Ctrl+L` | Load Policy | File dialog opens |
| `Ctrl+R` | Reset | Q-table and chart clear |
| `Ctrl+E` | Export CSV | File dialog opens |
| `Delete` | Clear selected cell | Clicked cell becomes white |

---

## 11. Menu Bar

### File menu
- **Save Policy** → same as Ctrl+S
- **Load Policy** → same as Ctrl+L
- **Exit** → closes application cleanly

### Edit menu
- **Reset Grid** → restores default 10×10 empty grid with Start/Goal

### Help menu
- **About** → popup showing `2D Drone Pathfinding RL Simulation v1.00`

---

## 12. Error Handling Tests

### 12.1 Load a corrupted JSON

1. Create a file `policies/bad.json` containing `{invalid json`
2. Click **Load Policy** → select `bad.json`
3. **Expected:** Error message in status bar — no crash ✅

### 12.2 Train with no grid loaded

The app always loads a default grid, so training always works.
If you somehow reach a state with no grid, the status bar should show a warning.

### 12.3 Check the log file

```bash
cat /Users/yona/code/RL/Drones/drone-rl/logs/drone_rl.log
```

Warnings from corrupted files are logged here ✅

---

## 13. Run the Full Automated Test Suite

To confirm nothing is broken after manual changes:

```bash
cd /Users/yona/code/RL/Drones/drone-rl

# Full test suite (177 tests)
uv run pytest -p no:cov -o "addopts=" -v

# Acceptance scenarios only (15 tests)
uv run pytest tests/integration/test_scenarios/ -v -p no:cov -o "addopts="

# Linting (zero violations required)
uv run ruff check src/ tests/

# Line-count audit (all files must be ≤150 lines)
find src/ tests/ -name "*.py" -exec sh -c \
  'lines=$(wc -l < "$1"); if [ "$lines" -gt 150 ]; then echo "❌ $1: $lines lines"; fi' _ {} \;
```

---

## 14. Run the Parameter Sensitivity Notebook

```bash
cd /Users/yona/code/RL/Drones/drone-rl
uv run jupyter notebook notebooks/parameter_sensitivity.ipynb
```

The notebook runs a grid sweep over alpha, gamma, epsilon values and generates:
- Success rate heatmaps
- Box plots by epsilon
- Convergence time-series curves
- Statistical summary table with recommended configuration

---

## Quick-Start Checklist

Use this checklist for a fast 5-minute smoke test:

```
[ ] uv sync           — dependencies installed
[ ] uv run python -m drone_rl.main  — app launches
[ ] Place Building, Trap, Crosswind obstacles on grid
[ ] Set 500 episodes, click Train
[ ] Convergence chart shows upward trend
[ ] Heatmap fills with colour
[ ] Policy arrows point toward goal
[ ] Ctrl+S saves policy, Ctrl+R resets, Ctrl+L reloads
[ ] Edit → Reset Grid restores clean grid
[ ] uv run pytest -p no:cov -o "addopts=" -q  — 177 passed
```

---

*2D Drone Pathfinding RL Simulation — v1.0.0*
*Dr. Yoram Segal Professional Software Guidelines v3.00 compliant*

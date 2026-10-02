# AI Lab 02 — Intelligent Agents: The 2D Vacuum-Cleaner World

Coursework for the **Artificial Intelligence Lab** (BSCS, Air University). This lab is about **rational agents**: how an agent perceives its environment, keeps (or doesn't keep) an internal model of the world, and acts to maximise a performance measure. It has two parts — a programming task that pits two agent designs against each other in a vacuum-cleaner world, and a written PEAS analysis of a real-world agent idea.

## Lab Objectives

- Model a simple environment with percepts, actions, and a performance measure.
- Implement and compare two agent architectures from the AIMA taxonomy:
  - a **model-based reflex agent**, and
  - a **goal-based agent** that plans with breadth-first search (BFS).
- Observe how **partial observability** limits what even a planning agent can achieve.
- Formulate a complete **PEAS description** (Performance measure, Environment, Actuators, Sensors) for a real-world agent and justify which agent type fits it best.

## Tasks

### Task 01 — 2D Vacuum-Cleaner World (`task1_2d_vacuum.py`)

A 3×3 room where every cell is either `Dirty` or `Clean`. The agent starts at `(0, 0)` with five dirty cells — `(0,1)`, `(1,0)`, `(1,2)`, `(2,0)`, `(2,2)`. Available actions are `Up`, `Down`, `Left`, `Right`, `Suck`, and `NoOp`.

**Performance measure:** `+10` for each dirt removed, `−1` for each move (`Suck` and `NoOp` are free).

Both agents run on the *same* initial layout, and the program prints a step-by-step trace of percepts, actions, internal state, and score for a fair comparison.

| Agent | How it works |
|---|---|
| **Model-Based Reflex Agent** | Keeps an internal model of every visited cell plus a visited set. If the current cell is dirty it sucks; otherwise it follows a fixed snake (boustrophedon) sweep to the next unvisited cell; it stops (`NoOp`) once the whole sweep is covered. |
| **Goal-Based Agent** | Goal: *every cell is known and clean*. It updates its model from each percept, sucks immediately on dirt (discarding any old plan), and otherwise uses **BFS** to plan the shortest path to the nearest unknown or dirty cell, executing the plan one step at a time. |

**Result:** both agents finish with the room completely clean and the **same score of 42**. That tie is the point of the exercise — the room is only *partially observable* (the agent perceives only its current cell), so even the goal-based agent must physically visit all 9 cells before it can prove its goal is satisfied. Planning cannot beat systematic coverage when nothing is known in advance.

### Task 02 — PEAS Description: Smart Irrigation Agent (written, in `242816.docx`)

A written analysis of a **Smart Irrigation Agent** — a system that decides on its own when and how much to water plants in a field or garden.

- **Performance:** plants stay healthy without over- or under-watering; minimal water and electricity use; no watering during rain; no plant deaths from wrong watering.
- **Environment:** a field divided into zones with different soils, weather (rain, heat, humidity, sunlight), a limited water tank, and plants at different growth stages.
- **Actuators:** per-zone water valves, a pump motor, sprinklers/drip pipes, a phone notification system for the farmer, and a watering logger.
- **Sensors:** soil-moisture, temperature/humidity, rain + weather forecast, water-flow (leak/blockage detection), and light sensors with a clock.

The report concludes this agent is best classified as a **utility-based agent**: it has several goals that conflict (save water vs. keep plants healthy vs. save electricity) and must choose the action with the best overall expected outcome under uncertainty — e.g. skipping watering when there is an 80% chance of rain. The full reasoning is in `242816.docx`.

## Tech Stack

- **Python 3** — standard library only (`collections.deque` for the BFS frontier). No external dependencies.
- Developed in PyCharm.

## Project Structure

```
ai-lab-02/
├── task1_2d_vacuum.py   # Task 01: environment + both agents + simulation driver
├── 242816.docx          # Lab report: Task 02 PEAS analysis (and Task 01 listing/output)
├── README.md
└── .gitignore
```

## How to Run

Requires Python 3. No packages to install.

```bash
python task1_2d_vacuum.py
```

The program runs both agents back-to-back on identical room layouts and prints:

1. the initial grid (`D` = dirty, `C` = clean, `[A]` = agent position),
2. a per-step trace — percept, chosen action, running score, and the agent's internal state,
3. the final grid, final performance score, and whether the room is fully clean,
4. a closing comparison of the two agents' scores.

**Sample final output:**

```
========================================================================
  COMPARISON
========================================================================
  Model-Based Reflex Agent : score = 42
  Goal-Based Agent         : score = 42
```

## Key Concepts Covered

- Rational agents and the AIMA agent taxonomy (reflex, model-based reflex, goal-based, utility-based)
- PEAS descriptions for specifying an agent's task environment
- Partial observability and why it forces exploration
- Internal state / world models
- Breadth-first search as a planning method
- Performance measures for comparing agent designs

## Author

**Hussnain Ahmad** — BSCS, Air University, Islamabad.
Artificial Intelligence Lab — Lab 02.

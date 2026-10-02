

from collections import deque

ROWS = 3
COLS = 3

MOVES = {
    'Up':    (-1,  0),
    'Down':  ( 1,  0),
    'Left':  ( 0, -1),
    'Right': ( 0,  1),
}


# -----------------------------------------------------------------------------
# STEP 1: THE ENVIRONMENT
# -----------------------------------------------------------------------------
class VacuumEnvironment2D:
    """A rows x cols room. Every cell is either 'Dirty' or 'Clean'."""

    def __init__(self, rows=ROWS, cols=COLS, dirty_cells=None, agent_start=(0, 0)):
        self.rows = rows
        self.cols = cols
        dirty_cells = set(dirty_cells or [])
        self.grid = {
            (r, c): ('Dirty' if (r, c) in dirty_cells else 'Clean')
            for r in range(rows) for c in range(cols)
        }
        self.agent_location = agent_start
        self.performance = 0          # +10 per dirt removed, -1 per move

    def percept(self):
        return (self.agent_location, self.grid[self.agent_location])

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def execute_action(self, action):
        if action == 'Suck':
            if self.grid[self.agent_location] == 'Dirty':
                self.grid[self.agent_location] = 'Clean'
                self.performance += 10

        elif action in MOVES:
            dr, dc = MOVES[action]
            r, c = self.agent_location
            nr, nc = r + dr, c + dc
            self.performance -= 1
            if self.in_bounds(nr, nc):
                self.agent_location = (nr, nc)
            else:
                print("        (bumped into a wall - stayed in place)")
        # 'NoOp' -> do nothing, no cost

    def is_clean(self):
        return all(v == 'Clean' for v in self.grid.values())

    def display(self, title="Grid state"):
        print(f"\n    {title}   (D = Dirty, C = Clean, [A] = agent here)")
        print("    " + "-" * (self.cols * 7 + 1))
        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                mark = 'D' if self.grid[(r, c)] == 'Dirty' else 'C'
                if (r, c) == self.agent_location:
                    row_cells.append(f"[A]{mark} ")
                else:
                    row_cells.append(f"  {mark}   ")
            print("    |" + "|".join(row_cells) + "|")
            print("    " + "-" * (self.cols * 7 + 1))


# -----------------------------------------------------------------------------
# STEP 2: MODEL-BASED REFLEX AGENT (4-directional)
# -----------------------------------------------------------------------------
class ModelBasedReflexAgent2D:
    """
    Keeps an INTERNAL MODEL of the room:
        self.model   -> what it learned about each visited cell
        self.visited -> which cells it has already been to
    Rules:
        1. current cell Dirty                  -> Suck
        2. else move to next unvisited cell of a fixed snake sweep
        3. whole sweep visited                 -> NoOp (stop)
    """

    name = "Model-Based Reflex Agent"

    def __init__(self, rows=ROWS, cols=COLS):
        self.rows = rows
        self.cols = cols
        self.model = {}
        self.visited = set()
        self.sweep = self._snake_path()
        self.index = 0

    def _snake_path(self):
        """Row 0 left->right, row 1 right->left, ... so consecutive cells touch."""
        path = []
        for r in range(self.rows):
            cols = range(self.cols) if r % 2 == 0 else range(self.cols - 1, -1, -1)
            for c in cols:
                path.append((r, c))
        return path

    @staticmethod
    def _step_towards(loc, target):
        (r, c), (tr, tc) = loc, target
        if tr < r:
            return 'Up'
        if tr > r:
            return 'Down'
        if tc < c:
            return 'Left'
        if tc > c:
            return 'Right'
        return 'NoOp'

    def program(self, percept):
        location, status = percept

        self.model[location] = status      # update internal state
        self.visited.add(location)

        if status == 'Dirty':              # Rule 1
            return 'Suck'

        while self.index < len(self.sweep) and self.sweep[self.index] in self.visited:
            self.index += 1                # Rule 2

        if self.index >= len(self.sweep):  # Rule 3
            return 'NoOp'

        return self._step_towards(location, self.sweep[self.index])

    def describe_state(self):
        return f"model has {len(self.model)}/{self.rows * self.cols} cells"


# -----------------------------------------------------------------------------
# STEP 3: GOAL-BASED AGENT (4-directional, plans with BFS)
# -----------------------------------------------------------------------------
class GoalBasedAgent2D:
    """
    GOAL: every cell is known AND Clean.
        1. update model from percept
        2. goal test -> NoOp if satisfied
        3. Dirty here -> Suck (discard old plan)
        4. else BFS to nearest unknown/dirty cell, execute plan one step at a time
    """

    name = "Goal-Based Agent"

    def __init__(self, rows=ROWS, cols=COLS):
        self.rows = rows
        self.cols = cols
        self.model = {}
        self.plan = []

    def _goal_reached(self):
        return (len(self.model) == self.rows * self.cols
                and all(v == 'Clean' for v in self.model.values()))

    def _is_interesting(self, cell):
        return cell not in self.model or self.model[cell] == 'Dirty'

    def _bfs_plan(self, start):
        """Breadth-first search -> shortest action list to nearest goal cell."""
        frontier = deque([(start, [])])
        explored = {start}
        while frontier:
            cell, actions = frontier.popleft()
            if cell != start and self._is_interesting(cell):
                return actions
            r, c = cell
            for action, (dr, dc) in MOVES.items():
                nxt = (r + dr, c + dc)
                if (0 <= nxt[0] < self.rows and 0 <= nxt[1] < self.cols
                        and nxt not in explored):
                    explored.add(nxt)
                    frontier.append((nxt, actions + [action]))
        return []

    def program(self, percept):
        location, status = percept

        self.model[location] = status          # 1

        if self._goal_reached():               # 2
            return 'NoOp'

        if status == 'Dirty':                  # 3
            self.plan = []
            return 'Suck'

        if not self.plan:                      # 4
            self.plan = self._bfs_plan(location)

        return self.plan.pop(0) if self.plan else 'NoOp'

    def describe_state(self):
        plan_txt = "->".join(self.plan) if self.plan else "(none)"
        return f"model has {len(self.model)}/{self.rows * self.cols} cells, plan: {plan_txt}"


# -----------------------------------------------------------------------------
# STEP 4: SIMULATION DRIVER
# -----------------------------------------------------------------------------
def run_agent(agent, environment, max_steps=60):
    print("=" * 72)
    print(f"  RUNNING: {agent.name}   on a {environment.rows}x{environment.cols} grid")
    print("=" * 72)
    environment.display("Initial grid")
    print()

    for step in range(1, max_steps + 1):
        percept = environment.percept()
        action = agent.program(percept)

        print(f"  Step {step:>2} | Percept: location={percept[0]}, status={percept[1]:<5}"
              f" | Action: {action:<6} | Score: {environment.performance}")
        print(f"          | Internal state: {agent.describe_state()}")

        if action == 'NoOp':
            print("\n  >> Agent has stopped: nothing left to do.")
            break

        environment.execute_action(action)
    else:
        print("\n  >> Step limit reached.")

    environment.display("FINAL grid state")
    print(f"\n  Final performance score : {environment.performance}")
    print(f"  Room completely clean?  : {environment.is_clean()}")
    print()
    return environment.performance


# -----------------------------------------------------------------------------
# STEP 5: MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    DIRTY = [(0, 1), (1, 0), (1, 2), (2, 0), (2, 2)]
    START = (0, 0)

    env_a = VacuumEnvironment2D(ROWS, COLS, DIRTY, START)
    score_a = run_agent(ModelBasedReflexAgent2D(ROWS, COLS), env_a)

    env_b = VacuumEnvironment2D(ROWS, COLS, DIRTY, START)
    score_b = run_agent(GoalBasedAgent2D(ROWS, COLS), env_b)

    print("=" * 72)
    print("  COMPARISON")
    print("=" * 72)
    print(f"  Model-Based Reflex Agent : score = {score_a}")
    print(f"  Goal-Based Agent         : score = {score_b}")
    print("""
  Both agents score the same here, and that is expected: the room is only
  PARTIALLY OBSERVABLE, so even the goal-based agent has to physically visit
  all 9 cells before it can prove its goal is satisfied.

 
""")
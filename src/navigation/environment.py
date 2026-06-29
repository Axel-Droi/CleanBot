from __future__ import annotations

import random
from enum import IntEnum

import numpy as np


class Action(IntEnum):
    FORWARD     = 0
    TURN_LEFT   = 1
    TURN_RIGHT  = 2
    COLLECT     = 3


class Heading(IntEnum):
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3


_DELTA: dict[Heading, tuple[int, int]] = {
    Heading.NORTH: (-1,  0),
    Heading.EAST:  ( 0,  1),
    Heading.SOUTH: ( 1,  0),
    Heading.WEST:  ( 0, -1),
}

CELL_EMPTY    = 0
CELL_TRASH    = 1
CELL_OBSTACLE = 2

_HEADING_SYM = {Heading.NORTH: "^", Heading.EAST: ">", Heading.SOUTH: "v", Heading.WEST: "<"}
_CELL_SYM    = {CELL_EMPTY: ".", CELL_TRASH: "T", CELL_OBSTACLE: "#"}


class GridEnvironment:
    """
    20×20 grid world for CleanBot navigation simulation.

    Reward structure (from README):
      +10  successful trash pickup
      +1   first visit to a new cell (exploration)
      -5   collision with obstacle or wall
      -1   COLLECT on an empty cell (wasted action)
      -0.1 each step (time penalty — encourages efficiency)
    """

    def __init__(
        self,
        size: int = 20,
        trash_density: float = 0.12,
        obstacle_density: float = 0.05,
        max_steps: int = 500,
        seed: int | None = None,
    ):
        self.size             = size
        self.trash_density    = trash_density
        self.obstacle_density = obstacle_density
        self.max_steps        = max_steps
        self._rng             = random.Random(seed)
        self.reset()

    # ------------------------------------------------------------------
    def reset(self) -> tuple[int, int, int]:
        self.grid = np.zeros((self.size, self.size), dtype=np.int8)

        for r in range(self.size):
            for c in range(self.size):
                if self._rng.random() < self.obstacle_density:
                    self.grid[r, c] = CELL_OBSTACLE

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r, c] == CELL_EMPTY and self._rng.random() < self.trash_density:
                    self.grid[r, c] = CELL_TRASH

        center = self.size // 2
        self.grid[center, center] = CELL_EMPTY   # robot start is always clear
        self.row     = center
        self.col     = center
        self.heading = Heading.NORTH

        self.visited: set[tuple[int, int]] = {(self.row, self.col)}
        self.total_trash = int(np.sum(self.grid == CELL_TRASH))
        self.collected   = 0
        self.steps       = 0

        return self._state()

    # ------------------------------------------------------------------
    def step(self, action: Action) -> tuple[tuple[int, int, int], float, bool, dict]:
        self.steps += 1
        reward = -0.1  # time penalty every step

        if action == Action.FORWARD:
            dr, dc = _DELTA[self.heading]
            nr, nc = self.row + dr, self.col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr, nc] != CELL_OBSTACLE:
                self.row, self.col = nr, nc
                if (self.row, self.col) not in self.visited:
                    reward += 1.0
                    self.visited.add((self.row, self.col))
            else:
                reward -= 5.0  # wall or obstacle collision

        elif action == Action.TURN_LEFT:
            self.heading = Heading((int(self.heading) - 1) % 4)

        elif action == Action.TURN_RIGHT:
            self.heading = Heading((int(self.heading) + 1) % 4)

        elif action == Action.COLLECT:
            if self.grid[self.row, self.col] == CELL_TRASH:
                self.grid[self.row, self.col] = CELL_EMPTY
                self.collected += 1
                reward += 10.0
            else:
                reward -= 1.0

        done = self.steps >= self.max_steps or self.collected >= self.total_trash
        return self._state(), reward, done, {"collected": self.collected, "steps": self.steps}

    # ------------------------------------------------------------------
    def _state(self) -> tuple[int, int, int]:
        return (self.row, self.col, int(self.heading))

    def render(self) -> str:
        rows = []
        for r in range(self.size):
            line = ""
            for c in range(self.size):
                if r == self.row and c == self.col:
                    line += _HEADING_SYM[self.heading]
                else:
                    line += _CELL_SYM[int(self.grid[r, c])]
            rows.append(line)
        return "\n".join(rows)

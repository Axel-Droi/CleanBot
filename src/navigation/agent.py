from __future__ import annotations

import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np

from src.navigation.environment import Action


class QLearningAgent:
    """
    Tabular Q-Learning agent for CleanBot grid navigation.

    Q(s, a) ← Q(s, a) + α [ r + γ max_a' Q(s', a') − Q(s, a) ]

    State  = (row, col, heading)   →  20×20×4 = 1 600 distinct states
    Action = FORWARD | TURN_LEFT | TURN_RIGHT | COLLECT  (4 actions)
    """

    def __init__(
        self,
        n_actions: int      = len(Action),
        lr: float           = 0.1,
        gamma: float        = 0.95,
        epsilon: float      = 1.0,
        epsilon_min: float  = 0.05,
        epsilon_decay: float = 0.995,
    ):
        self.n_actions     = n_actions
        self.lr            = lr
        self.gamma         = gamma
        self.epsilon       = epsilon
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table: dict = defaultdict(lambda: np.zeros(n_actions, dtype=np.float32))

    # ------------------------------------------------------------------
    def choose_action(self, state: tuple) -> int:
        if np.random.random() < self.epsilon:
            return int(np.random.randint(self.n_actions))
        return int(np.argmax(self.q_table[state]))

    def update(
        self,
        state: tuple,
        action: int,
        reward: float,
        next_state: tuple,
        done: bool,
    ) -> None:
        current_q = self.q_table[state][action]
        target    = reward if done else reward + self.gamma * float(np.max(self.q_table[next_state]))
        self.q_table[state][action] += self.lr * (target - current_q)

    def decay_epsilon(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # ------------------------------------------------------------------
    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "q_table":       dict(self.q_table),
                    "epsilon":       self.epsilon,
                    "n_actions":     self.n_actions,
                    "lr":            self.lr,
                    "gamma":         self.gamma,
                    "epsilon_min":   self.epsilon_min,
                    "epsilon_decay": self.epsilon_decay,
                },
                f,
            )

    def load(self, path: Path | str) -> None:
        with open(Path(path), "rb") as f:
            data = pickle.load(f)
        self.n_actions     = data["n_actions"]
        self.lr            = data["lr"]
        self.gamma         = data["gamma"]
        self.epsilon       = data["epsilon"]
        self.epsilon_min   = data["epsilon_min"]
        self.epsilon_decay = data["epsilon_decay"]
        self.q_table       = defaultdict(
            lambda: np.zeros(self.n_actions, dtype=np.float32),
            {k: np.array(v, dtype=np.float32) for k, v in data["q_table"].items()},
        )

#!/usr/bin/env python3
"""
Train the Q-Learning navigation agent in simulation.

Usage:
  python src/navigation/train_agent.py --episodes 1000
  python src/navigation/train_agent.py --episodes 5000 --render
  python src/navigation/train_agent.py --episodes 2000 --size 30
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

# allow running from repo root or from src/navigation/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.navigation.environment import Action, GridEnvironment
from src.navigation.agent import QLearningAgent

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


def train(episodes: int, grid_size: int = 20, render: bool = False) -> QLearningAgent:
    env   = GridEnvironment(size=grid_size, seed=42)
    agent = QLearningAgent()

    ep_rewards:   list[float] = []
    ep_collected: list[int]   = []
    best_pct = 0.0

    for ep in range(1, episodes + 1):
        state  = env.reset()
        total_reward = 0.0
        done   = False

        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, info = env.step(Action(action))
            agent.update(state, action, reward, next_state, done)
            state        = next_state
            total_reward += reward

        agent.decay_epsilon()
        ep_rewards.append(total_reward)
        ep_collected.append(info["collected"])

        pct = info["collected"] / max(env.total_trash, 1) * 100
        if pct > best_pct:
            best_pct = pct
            agent.save(MODELS_DIR / "nav_agent_best.pkl")

        if ep % 100 == 0:
            avg_r   = float(np.mean(ep_rewards[-100:]))
            avg_col = float(np.mean(ep_collected[-100:]))
            avg_pct = avg_col / max(env.total_trash, 1) * 100
            print(
                f"Ep {ep:5d}/{episodes}  "
                f"avg_reward={avg_r:8.1f}  "
                f"avg_collected={avg_col:.1f}/{env.total_trash} ({avg_pct:.0f}%)  "
                f"ε={agent.epsilon:.3f}"
            )

        if render and ep % 500 == 0:
            print(f"\n── Episode {ep} ──")
            print(env.render())

    agent.save(MODELS_DIR / "nav_agent_final.pkl")
    print(f"\nDone. Saved to {MODELS_DIR}/")
    print(f"Best single-episode collection: {best_pct:.1f}% of trash")

    _plot(ep_rewards, ep_collected, env.total_trash, episodes)
    return agent


def _plot(rewards: list, collected: list, total_trash: int, episodes: int) -> None:
    try:
        import matplotlib.pyplot as plt

        window = min(50, episodes // 10 or 1)
        kernel = np.ones(window) / window

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
        fig.suptitle("CleanBot Q-Learning Training", fontsize=13, fontweight="bold")

        ax1.plot(rewards, alpha=0.25, color="#4299E1", linewidth=0.8)
        ax1.plot(np.convolve(rewards, kernel, mode="valid"), color="#4299E1", linewidth=2)
        ax1.set_title("Episode Reward")
        ax1.set_xlabel("Episode")
        ax1.set_ylabel("Total Reward")
        ax1.grid(alpha=0.3)

        ax2.plot(collected, alpha=0.25, color="#48BB78", linewidth=0.8)
        ax2.plot(np.convolve(collected, kernel, mode="valid"), color="#48BB78", linewidth=2)
        ax2.axhline(total_trash, color="#FC8181", linestyle="--", linewidth=1.5,
                    label=f"All trash ({total_trash})")
        ax2.set_title("Items Collected per Episode")
        ax2.set_xlabel("Episode")
        ax2.set_ylabel("Items Collected")
        ax2.legend()
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        out = Path(__file__).resolve().parents[2] / "models" / "training_curve.png"
        plt.savefig(str(out), dpi=150)
        print(f"Training curve → {out}")
    except ImportError:
        pass  # matplotlib not installed


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CleanBot Q-Learning navigation agent")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of training episodes")
    parser.add_argument("--size",     type=int, default=20,   help="Grid size (NxN)")
    parser.add_argument("--render",   action="store_true",    help="Print grid every 500 episodes")
    args = parser.parse_args()
    train(args.episodes, grid_size=args.size, render=args.render)


if __name__ == "__main__":
    main()

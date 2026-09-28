import numpy as np
from .model import NullModel

def simulate_draws(model: NullModel, runs: int, seed: int) -> np.ndarray:
    if runs <= 0:
        raise ValueError("runs must be positive")
    rng = np.random.default_rng(seed)
    return np.array([model.draw(rng) for _ in range(runs)], dtype=int)

def draw_sums(draws: np.ndarray) -> np.ndarray:
    return draws.sum(axis=1)

def parity_counts(draws: np.ndarray) -> np.ndarray:
    return (draws % 2 == 1).sum(axis=1)

def consecutive_counts(draws: np.ndarray) -> np.ndarray:
    return np.array([int(np.sum(np.diff(np.sort(d)) == 1)) for d in draws], dtype=int)

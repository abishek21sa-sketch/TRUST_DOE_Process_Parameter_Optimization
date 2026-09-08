from __future__ import annotations
import itertools
import numpy as np
from .domain import ProcessSpace


def factorial_points(space: ProcessSpace, center: bool = True) -> np.ndarray:
    coded = np.array(list(itertools.product([-1.0, 1.0], repeat=space.dimension)), dtype=float)
    if center:
        coded = np.vstack([coded, np.zeros((1, space.dimension))])
    return np.array([space.denormalize(row) for row in coded])


def latin_hypercube(space: ProcessSpace, n: int, seed: int = 11) -> np.ndarray:
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    d = space.dimension
    u = rng.random((n, d))
    result = np.empty_like(u)
    for j in range(d):
        perm = rng.permutation(n)
        result[:, j] = (perm + u[:, j]) / n
    z = 2.0 * result - 1.0
    return np.array([space.denormalize(row) for row in z])


def quadratic_features(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    if z.ndim == 1:
        z = z[None, :]
    cols = [np.ones(len(z))]
    cols.extend([z[:, i] for i in range(z.shape[1])])
    cols.extend([z[:, i]**2 for i in range(z.shape[1])])
    for i in range(z.shape[1]):
        for j in range(i+1, z.shape[1]):
            cols.append(z[:, i]*z[:, j])
    return np.column_stack(cols)


def information_logdet(z: np.ndarray, ridge: float = 1e-8) -> float:
    X = quadratic_features(z)
    M = X.T @ X + ridge*np.eye(X.shape[1])
    sign, logdet = np.linalg.slogdet(M)
    if sign <= 0:
        raise RuntimeError("Information matrix is not positive definite")
    return float(logdet)
